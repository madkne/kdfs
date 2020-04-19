


from libs.Daemon import Daemon
from libs.Config import Config
from server.KDFSServer import KDFSServer
from commands.identify import identifyCommand

import sys, time
import json
import signal
import sys
 
KDFS_SERVER = None
# ------------------------------------------------
class KDFSDaemon(Daemon):
        def run(self):
                # read kdfs config file
                KDFSConfig = Config('kdfs.conf')
                # KDFSConfig.read("kdfs.conf")
                print("KDFS SERVER (version {})".format(KDFSConfig.get('version','unknown')))
                # get kdfs server info
                info = json.loads(identifyCommand().response())
                print("MAC Address is {} on {}({})".format(info['macaddr'],info['os'],info['arch']))
                # check if server is queen
                if KDFSConfig.getBoolean('is_queen',False):
                        print("*** THIS SERVER RUN AS QUEEN ***")
                print("\n")
                # print(KDFSConfig.getItems())
                # run kdfs server'
                server = KDFSServer(KDFSConfig)
            
 
# def signal_handler(signal, frame):
#         exit(0)

# signal.signal(signal.SIGINT, signal_handler)
# ------------------------------------------------
# when start kdfs daemon program
if __name__ == "__main__":
        daemon = KDFSDaemon('/tmp/kdfs-daemon.pid')
        if len(sys.argv) == 2:
                if 'start' == sys.argv[1]:
                        daemon.start()
                elif 'stop' == sys.argv[1]:
                        daemon.stop()
                elif 'restart' == sys.argv[1]:
                        daemon.restart()
                else:
                        print("Unknown command")
                        exit(2)
                #=>exit sunccessfully
                exit(0)
        else:
                print("usage: {} start|stop|restart".format(sys.argv[0]))
                exit(2)

