
from libs.Config import Config
from server.KDFSProtocol import KDFSProtocol
from server.ServerUtils import ServerUtils
from server.ClientThread import ClientThread

# import thread module 
import socket
import multiprocessing
import threading
import json
# from socketserver import ThreadingMixIn 

class KDFSServer:
    HOST_NAME : str
    SERVER_PORT : int
    CLIENT_PORT : int
    LOCALSERVERTHREAD :multiprocessing.Process
    SERVER_SOCKET : socket.socket = None
    CLIENT_SOCKET : socket.socket = None
    IS_QUEEN = False
    QUEEN_IP = ''
    CLIENT_IP = ''
    QUEEN = None
    MAX_LISTEN = 1
    CLIENT_THREADS = []
    KDFS_CONFIG : Config = None
    KDFS_START_IP = ''
    KDFS_END_IP = ''
    CHUNK_SIZE = 1024
    # print_lock = threading.Lock()
    # -------------------------------------------
    def __init__(self,config : Config):
        self.HOST_NAME = '0.0.0.0'
        # print("fffff:",config.index('queen_port',0,len(config)))
        self.SERVER_PORT = config.getInteger('queen_port',4040)
        self.CLIENT_PORT = config.getInteger('client_port',4041)
        self.KDFS_CONFIG = config
        self.KDFS_START_IP = config.get('nodes_start_ip','192.168.0.0')
        self.KDFS_END_IP = config.get('nodes_end_ip','192.168.5.255')
        self.CHUNK_SIZE = config.getInteger('chunk_size',1024)
        # get client ip address
        self.CLIENT_IP = self.KDFS_CONFIG.get('client_ip','127.0.0.1')
        # check if this node server is queen
        if config.getBoolean('is_queen',False):
            from server.KDFSQueen import KDFSQueen
            self.IS_QUEEN = True
            self.QUEEN = KDFSQueen(config)
            self.MAX_LISTEN = config.getInteger('queen_max_nodes',1)
        # check for ports is already use
        if ServerUtils.checkPortInUse(self.CLIENT_PORT,self.CLIENT_IP) or ServerUtils.checkPortInUse(self.SERVER_PORT,self.HOST_NAME):
            print("(KDFS) One of \"{} on {}\" or \"{} on {}\" ports are already use!".format(self.SERVER_PORT,self.HOST_NAME, self.CLIENT_PORT,self.CLIENT_IP))
            return  
        # run local socket client in another thread!
        # self.LOCALSERVERTHREAD = threading.Thread(target=self._runLocalServer)
        self.LOCALSERVERTHREAD = multiprocessing.Process(target=self._runLocalServer)
        self.LOCALSERVERTHREAD.start()
        # run global socket server
        self._runGlobalServer()
    # -------------------------------------------
    def _runLocalServer(self):
        # create a socket object
        if self.CLIENT_SOCKET is None:
            # AF_INET == ipv4
            # SOCK_STREAM == TCP
            self.CLIENT_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                               
        # bind to the port
        try:
            self.CLIENT_SOCKET.bind((self.CLIENT_IP, self.CLIENT_PORT))  
            self.CLIENT_SOCKET.listen(1)
        except:
            print("(client) Can not bind local server on {} port".format(self.CLIENT_PORT))
            return
        # self.SERVER_SOCKET.settimeout(1000)    
        print("(client) KDFS Client Socket listenning on {}:{}".format(self.CLIENT_IP,self.CLIENT_PORT))
        # listen on any request
        while True:
            try:
                if self.CLIENT_SOCKET is None: break
                # accept connections from outside
                (clientsocket, (ip,port)) = self.CLIENT_SOCKET.accept()
                print(f"(client) Connection has been established.")
                # Receive the data in small chunks and retransmit it
                while True:
                    try:
                        #=>get a command with parameters as json
                        chunk_size = self.KDFS_CONFIG.getInteger('chunk_size',1024)
                        command = KDFSProtocol.receiveMessage(clientsocket,chunk_size)
                        # check for empty command
                        if command == '':
                            print("(client) No command received. shutting down socket...")
                            break
                        print('(client) Command Request received : {}'.format(command['command']))
                        # get queen ip address
                        if self.QUEEN_IP == '':
                            print("(client) Searching for queen server on local network...")
                            self.findQueenIP()
                        # if not found queen server
                        if self.QUEEN_IP == '':
                            print("(client) Not Found Queen Server!")
                            break
                        else:
                            print("(client) Queen Server IP is {}".format(self.QUEEN_IP))
                        # send command to queen server
                        print("(client) Sending client command to Queen Server...")
                        queensocket = ServerUtils.socketConnect(self.QUEEN_IP,self.SERVER_PORT)
                        try:
                            # send client command to queen server
                            KDFSProtocol.sendMessage(queensocket,chunk_size,json.dumps(command))
                            # get command response as json
                            response = KDFSProtocol.receiveMessage(queensocket,chunk_size)
                            # close queen socket
                            queensocket.close()
                            # send response to client program
                            KDFSProtocol.sendMessage(clientsocket,chunk_size,json.dumps(response))
                        except Exception as e:
                            print("(client) connection closed by queen.",e)
                            break

                    except Exception as e:
                        print("(client) connection closed by client.",e)
                        # raise
                        break
            except KeyboardInterrupt:
                break
            except Exception as e:
                print("(client) raise an exception :",e)
                continue
                
        # Clean up the connection
        self.CLIENT_SOCKET.close()

    # -------------------------------------------
    def _runGlobalServer(self):
        # create a socket object
        if self.SERVER_SOCKET is None:
            # AF_INET == ipv4
            # SOCK_STREAM == TCP
            self.SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                               
        # bind to the port
        try:
            self.SERVER_SOCKET.bind((self.HOST_NAME, self.SERVER_PORT))  
            self.SERVER_SOCKET.listen(self.MAX_LISTEN)
        except:
            print("(server) Can not bind server on {} port".format(self.SERVER_PORT))
            return
        # self.SERVER_SOCKET.settimeout(1000)    
        print("(server) KDFS Server Socket listenning on {}:{}".format(self.HOST_NAME,self.SERVER_PORT))
        # listen on any request
        while True:
            try:
                if self.SERVER_SOCKET is None: break
                # accept connections from outside
                (clientsocket, (ip,port)) = self.SERVER_SOCKET.accept()
                print(f"(server) Connection from {ip} has been established.")

                newthread = ClientThread(ip,port,clientsocket,self.KDFS_CONFIG) 
                newthread.start() 
                self.CLIENT_THREADS.append(newthread) 
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print("(server) raise an exception :",e)
                continue
                
        # Clean up the connection
        self.terminate()

    # -------------------------------------------
    def terminate(self):
        print()
        # terminate client socket
        if self.CLIENT_SOCKET is not None:
            # self.CLIENT_SOCKET.close()
            self.CLIENT_SOCKET.shutdown()
        self.LOCALSERVERTHREAD.kill()
        print("(client) KDFS Local Server Shutted down.")
        # terminate server socket
        if self.SERVER_SOCKET is not None:
            print("(server) KDFS Server is Shutting down...")
            # kill all client threads
            try:
                for t in self.CLIENT_THREADS: 
                    t.join()
            except:
                pass
            # close server connection socket
            self.SERVER_SOCKET.close()  
            self.SERVER_SOCKET = None  
            # exit system
            exit(0)
    # -------------------------------------------
    def findQueenIP(self):
        # if queen ip is exist, ignore!
        if self.QUEEN_IP != '': 
            return 
        # get queen ip from config,if exist
        queenIP = self.KDFS_CONFIG.get('queen_ip','127.0.0.1')
        # validate old queen IP
        if ServerUtils.checkQueenByIP(queenIP,self.SERVER_PORT,self.CHUNK_SIZE):
            self.QUEEN_IP = queenIP
            return
        # check if this system has queen server!
        if self.IS_QUEEN:
            self.QUEEN_IP = '127.0.0.1'
        # scan all up hosts in local network
        else:
            # get all IPs between start_ip and end_ip
            IPpool = ServerUtils.getIPAddressesPool(self.KDFS_START_IP,self.KDFS_END_IP)
            # iterate all IPs of pool
            for IP in IPpool:
                if ServerUtils.checkQueenByIP(IP,self.SERVER_PORT,self.CHUNK_SIZE):
                    self.QUEEN_IP = IP
                    break

        # update config queen IP
        self.KDFS_CONFIG.updateItem('queen_ip',self.QUEEN_IP)

    # -------------------------------------------

