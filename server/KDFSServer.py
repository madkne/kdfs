
from libs.Config import Config
from server.KDFSQueen import KDFSQueen
import socket
# import thread module 
from threading import Thread 
from socketserver import ThreadingMixIn 

class KDFSServer:
    HOST_NAME : str
    PORT_NUMBER : int
    SERVER_SOCKET : socket.socket = None
    IS_QUEEN = False
    QUEEN : KDFSQueen = None
    MAX_LISTEN = 1
    CLIENT_THREADS = []
    # print_lock = threading.Lock()
    # -------------------------------------------
    def __init__(self,config : Config):
        self.HOST_NAME = '0.0.0.0'
        # print("fffff:",config.index('queen_port',0,len(config)))
        self.PORT_NUMBER = config.getInteger('queen_port',4040)
        # check if this node server is queen
        if config.getBoolean('is_queen',False):
            self.IS_QUEEN = True
            self.QUEEN = KDFSQueen(self.PORT_NUMBER,config.get('nodes_start_ip','192.168.0.0'),config.get('nodes_end_ip','192.168.2.255'))
            self.MAX_LISTEN = config.getInteger('queen_max_nodes',1)
        # run socket server
        self._runServer()

    # -------------------------------------------
    def _runServer(self):
        # create a socket object
        if self.SERVER_SOCKET is None:
            # AF_INET == ipv4
            # SOCK_STREAM == TCP
            self.SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                                 
        # bind to the port
        self.SERVER_SOCKET.bind((self.HOST_NAME, self.PORT_NUMBER))  
        self.SERVER_SOCKET.listen(self.MAX_LISTEN)
        # self.SERVER_SOCKET.settimeout(1000)    
        print("(server) KDFS Server Socket listenning on {}:{}".format(self.HOST_NAME,self.PORT_NUMBER))
        # listen on any request
        while True:
            try:
                if self.SERVER_SOCKET is None: break
                # accept connections from outside
                (clientsocket, (ip,port)) = self.SERVER_SOCKET.accept()
                print(f"(server) Connection from {ip} has been established.")

                newthread = ClientThread(ip,port,clientsocket) 
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
            # close server connection socket
            self.SERVER_SOCKET.close()  
            self.SERVER_SOCKET = None  
    # -------------------------------------------

# **************************************************************
class ClientThread(Thread): 
 
    def __init__(self,ip:str,port:int,clientsocket:socket.socket): 
        Thread.__init__(self) 
        self.ip = ip 
        self.port = port 
        self.socket = clientsocket
        print(f"(server) New server socket thread started for {ip}")
 
    def run(self): 
        while True:
            try:
                if not self.socket: break
                data = self.socket.recv(1024).decode('utf-8')
                print('Request received : {}'.format(data))
                if data :
                    self.socket.send('hello back!'.encode('utf-8'))
                else:
                    print("not data...")
                    self.socket.close()
                
            except Exception as e:
                print("connection closed by client.",e)
                break
                # socket.close(1)
                # break
                # raise