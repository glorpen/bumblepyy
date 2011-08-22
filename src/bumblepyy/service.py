'''
Created on 21-08-2011

@author: arkus
'''


from subprocess import Popen
import subprocess
import threading
import os
import signal
import dbus.service

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
        
        print "Xorg server initiated"
    
    def stop(self):
        print "stopping"
        if self._thread != None:
            self.proc.send_signal(signal.SIGTERM)
            self._thread.join(timeout=5)
            if self._thread != None and self._thread.isAlive():
                print "X server still running, killing"
                self.proc.kill()
                self._thread.join()
        
        return True
    
    def _run(self):
        self.proc = Popen("X "+self.args, shell=True, stderr=subprocess.PIPE, env={
            "LD_LIBRARY_PATH": self._library_path
        })
        
        for line in self.proc.stderr:
            print line
        
        self.proc.stderr.close()
        self.proc.kill()
        print self.proc.wait()
        
        print "X died"
        
        self._proc = None
        self._thread = None
        
    def start(self):
        print "starting"
        if self.running():
            raise RuntimeError("Server already running")
        
        self._thread = threading.Thread(target=self._run)
        self._thread.start()
        
        return True
    
    def restart(self):
        print "restarting"
        if self.running:
            self.stop()
        return self.start()
        
    def running(self):
        return self._thread != None
    
class BumblePyyService(dbus.service.Object):
    def __init__(self, config_path):
        self.config = Config(config_path)
        
        self.xorg_server = XorgServer(self.config)
        
        session_bus = dbus.SystemBus()
        self.name = dbus.service.BusName("org.bumblepyy", session_bus)
        
        dbus.service.Object.__init__(self, session_bus, '/BumblePyy')
        
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
            raise RuntimeError("server canot be stopped")
        
        return True
