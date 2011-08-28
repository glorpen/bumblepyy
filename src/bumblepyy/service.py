'''
Created on 21-08-2011

@author: arkus
'''


from subprocess import Popen
import syslog, time
from syslog import syslog as log
import subprocess, threading, signal
import dbus.service
import dbus.mainloop.glib

import gobject
gobject.threads_init()

from bumblepyy.config import Config

class XorgServer(object):
    def __init__(self, config):
        self.args = ":%s -config %s -sharevts -nolisten tcp -noreset -configdir /dev/null %s" % (
            config.x_display,
            config.x_config,
            config.system.x_args
        )
        
        self._thread = None
        self._proc = None
        
        self._library_path = config.system.library_path
        
        log(syslog.LOG_INFO, "X.Org server ready")
    
    def stop(self):
        if self._thread != None and self._thread.isAlive():
            log(syslog.LOG_DEBUG, "Trying to stop X.Org...")
            self._proc.send_signal(signal.SIGTERM)
            self._thread.join(timeout=3)
            if self._thread.isAlive():
                log(syslog.LOG_WARNING, "X.Org couldn't be stopped, killing")
                self._proc.kill()
                self._thread.join(timeout=5)
                if self._thread.isAlive():
                    log(syslog.LOG_ERR, "X.Org couldn't be killed")
                    return False
                else:
                    log(syslog.LOG_WARNING, "X.Org killed")
            else:
                log(syslog.LOG_DEBUG, "X.Org stopped")
        
        return True
    
    def _run(self):
        self._proc = Popen("X "+self.args, shell=True, stderr=subprocess.PIPE, env={
            "LD_LIBRARY_PATH": self._library_path
        })
        
        for line in self._proc.stderr:
            log(syslog.LOG_DEBUG, "[xorg] %s" % (line.strip(),))
        
        self._proc.stderr.close()
        self._proc.kill()
        
        status = self._proc.wait()
        if status == 0:
            log(syslog.LOG_INFO, "X.Org was successfully stopped")
        else:
            log(syslog.LOG_WARNING, "X.Org ended with status %d" % (status,))
        
        self._proc = None
        
    def start(self):
        if self.running():
            return True
        
        log(syslog.LOG_INFO, "Starting X.Org server...")
        
        self._thread = threading.Thread(target=self._run)
        self._thread.start()
        
        time.sleep(1)
        
        if self._thread.isAlive():
            log(syslog.LOG_INFO, "X.Org server started")
        else:
            log(syslog.LOG_ERR, "X.Org server cannot be started")
        return self._thread.isAlive()
    
    def restart(self):
        if self.running:
            self.stop()
        return self.start()
        
    def running(self):
        return self._thread.isAlive() if self._thread != None else False
    
class BumblePyyService(dbus.service.Object):
    
    def __init__(self, config_path):
        log(syslog.LOG_INFO, "starting service...")
        self._prepare()
        
        self.config = Config(config_path)
        
        self.xorg_server = XorgServer(self.config)
        
        system_bus = dbus.SystemBus()
        self.name = dbus.service.BusName("org.bumblepyy", system_bus)
        
        dbus.service.Object.__init__(self, system_bus, '/BumblePyy')
        
    @dbus.service.method(dbus_interface='org.bumblepyy', in_signature='', out_signature='b')
    def prepareXorg(self):
        '''
        Returns True if X server is ready, False otherwise. Will block until started.
        '''
        
        if not self.xorg_server.running():
            return self.xorg_server.restart()
        
        return True
    
    @dbus.service.method(dbus_interface='org.bumblepyy', in_signature='', out_signature='b')
    def enable(self):
        return True
    
    @dbus.service.method(dbus_interface='org.bumblepyy', in_signature='', out_signature='b')
    def disable(self):
        if not self.xorg_server.stop():
            log(syslog.LOG_ERR, "X.Org server cannot be stopped")
        return False
        
        return True
    
    def shutdown(self, sig, frame):
        log(syslog.LOG_INFO, "shutdown requested")
        self.remove_from_connection()
        self.mainloop.quit()
        self.xorg_server.stop()
        syslog.closelog()
    
    def _prepare(self):
        syslog.openlog("bumblepyy")
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.mainloop = gobject.MainLoop()
        
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        
    def run(self):
        log(syslog.LOG_INFO, "running")
        self.mainloop.run()
        