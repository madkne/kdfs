
from libs.Config import Config
from server.KDFSQueen import KDFSQueen
from server.KDFSProtocol import KDFSProtocol
from commands.identify import identifyCommand
from commands.list import listCommand
from server.ServerUtils import ServerUtils
from commands.minimal import MinimalCommands

# import thread module 
import socket
import multiprocessing
import threading
import json
from socketserver import ThreadingMixIn 

class KDFSServer:
    HOST_NAME : str
    SERVER_PORT : int
    CLIENT_PORT : int
    LOCALSERVERTHREAD :multiprocessing.Process
    SERVER_SOCKET : socket.socket = None
    CLIENT_SOCKET : socket.socket = None
    IS_QUEEN = False
    QUEEN_IP = ''
    QUEEN : KDFSQueen = None
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
        # check if this node server is queen
        if config.getBoolean('is_queen',False):
            self.IS_QUEEN = True
            self.QUEEN = KDFSQueen(self.SERVER_PORT,self.KDFS_START_IP,self.KDFS_END_IP,config.getInteger('chunk_size',1024))
            self.MAX_LISTEN = config.getInteger('queen_max_nodes',1)
        # run local socket client in another thread!
        # self.LOCALSERVERTHREAD = threading.Thread(target=self._runLocalServer)
        self.LOCALSERVERTHREAD = multiprocessing.Process(target=self._runLocalServer)
        self.LOCALSERVERTHREAD.start()
        # run global socket server
        self._runGlobalServer()
    # -------------------------------------------
    def _runLocalServer(self):
        # get client ip address
        client_ip = self.KDFS_CONFIG.get('client_ip','127.0.0.1')
        # create a socket object
        if self.CLIENT_SOCKET is None:
            # AF_INET == ipv4
            # SOCK_STREAM == TCP
            self.CLIENT_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
        # check for port is already use
        # print('(debug) is use:',ServerUtils.checkPortInUse(self.CLIENT_PORT,client_ip))
        if ServerUtils.checkPortInUse(self.CLIENT_PORT,client_ip):
            print("(client) Port {} on {} is already use!".format(client_ip, self.CLIENT_PORT))
            return                              
        # bind to the port
        self.CLIENT_SOCKET.bind((client_ip, self.CLIENT_PORT))  
        self.CLIENT_SOCKET.listen(1)
        # self.SERVER_SOCKET.settimeout(1000)    
        print("(client) KDFS Client Socket listenning on {}:{}".format(client_ip,self.CLIENT_PORT))
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
        # check for port is already use
        if ServerUtils.checkPortInUse(self.CLIENT_PORT,self.HOST_NAME):
            print("(server) Port {} on {} is already use!".format(self.HOST_NAME, self.CLIENT_PORT))
            return                               
        # bind to the port
        self.SERVER_SOCKET.bind((self.HOST_NAME, self.SERVER_PORT))  
        self.SERVER_SOCKET.listen(self.MAX_LISTEN)
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
        if self.SERVER_SOCKET is not None:
            print("\n(server) KDFS Server is Shutting down...")
            # kill all client threads
            for t in self.CLIENT_THREADS: 
                t.join()
            # kill client server
            if self.CLIENT_SOCKET is not None:
                self.CLIENT_SOCKET.close() 
            self.LOCALSERVERTHREAD.kill()
            # close server connection socket
            self.SERVER_SOCKET.close()  
            self.SERVER_SOCKET = None  
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
# **************************************************************
class ClientThread(threading.Thread): 
 
    def __init__(self,ip:str,port:int,clientsocket:socket.socket,config:Config): 
        # Thread.__init__(self) 
        super(ClientThread, self).__init__()
        self._stop_event = threading.Event() 
        self.ip = ip 
        self.port = port 
        self.socket = clientsocket
        self.config = config
        print(f"(server) New server socket thread started for {ip}")
    # -----------------------------------
    def run(self): 
        # print("(debug) run client ...")
        while True:
            try:
                if not self.socket: break
                #=>get a command with parameters as json
                chunk_size = self.config.getInteger('chunk_size',1024)
                command = KDFSProtocol.receiveMessage(self.socket,chunk_size)
                # check for empty command
                if command == '':
                    print("(server) No command received. shutting down socket...")
                    self.socket.close()
                    break
                print('(server) Command Request received : {}'.format(command['command']))
                response = ''
                # get queen command response as json
                if command['send_by'] == 'queen':
                    response = self.getQueenCommandResponse(command['command'],command['params'])
                # get client command response as json (for queen!)
                elif self.config.getBoolean('is_queen',False):
                    response = self.getClientCommandResponse(command['command'],command['params'])
                # send response of command
                KDFSProtocol.sendMessage(self.socket,chunk_size,response)
                print("(server) Send response for {} node".format(command['send_by']))
                
            except Exception as e:
                print("(server) connection closed by client.(1)",e)
                print("(debug) response:",response)
                raise
                break
    # -----------------------------------
    def getClientCommandResponse(self,command : str,params:list=[]):
        # list command
        if command == 'list':
            return listCommand(params).response()
    # -----------------------------------
    def getQueenCommandResponse(self,command:str,params:dict={}):
        response = ''
        error = ''
        # identify command
        if command == 'identify':
            response = MinimalCommands.identifyCommand()
        # list command
        elif command == 'list':
            response = MinimalCommands.listCommand(params['path'],self.config.get('storage','/'))
            if type(response) is not list:
                error = response
                response = []

        return json.dumps(KDFSProtocol.sendResponseFormatter(response,[error]))
    # -----------------------------------
    def stop(self):
        self._stop_event.set()
    # -----------------------------------
    def stopped(self):
        return self._stop_event.is_set()