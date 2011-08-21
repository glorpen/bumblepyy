'''
Created on 21-08-2011

@author: arkus
'''

import sys
from traceback import print_exc

import dbus
import ConfigParser
import subprocess
from subprocess import Popen
import os

def run():
    config = ConfigParser.ConfigParser()
    config.read('bumblepyy.conf')
    
    env = dict(os.environ)
    env["LD_LIBRARY_PATH"] = config.get("service", "library_path")
    #[[ $VGL_COMPRESS =~ ^jpeg|rgb|yuv$ ]] && vglclient -detach &>/dev/null
    proc = Popen([
        "vglrun",
        "-c", config.get("optirun", "vgl_compress"),
        "-d", ":"+config.get("service", "x_display"),
        "-ld", config.get("service", "library_path"),
        "--" 
    ]+sys.argv[1:], shell=False, stderr=subprocess.PIPE, env=env)
    
    os.environ
    
    for line in proc.stderr:
        print line
    
    print repr(proc.wait())

def main():
    bus = dbus.SystemBus()

    try:
        remote_object = bus.get_object("org.bumblepyy", "/BumblePyy")
        iface = dbus.Interface(remote_object, "org.bumblepyy")
        
        print repr(iface.prepareXorg())
        run()
        
        #print repr(iface.__getattr__(m)())

    except dbus.DBusException:
        print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()