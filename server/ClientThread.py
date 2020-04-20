
from commands.minimal import MinimalCommands
from server.KDFSProtocol import KDFSProtocol
from server.ServerUtils import ServerUtils
from libs.Config import Config


import socket
import threading
import json




class ClientThread(threading.Thread): 
 
    def __init__(self,ip:str,port:int,clientsocket:socket.socket,config:Config): 
        # Thread.__init__(self) 
        super(ClientThread, self).__init__()
        self._stop_event = threading.Event() 
        self.ip = ip 
        self.port = port 
        self.socket = clientsocket
        self.config = config
        self.packetNumber = 0
        self.commandData = {}
        self.isPacketFile = False
        self.isBinaryFile = False
        print(f"(server) New server socket thread started for {ip}")
    # -----------------------------------
    def run(self): 
        # print("(debug) run client ...")
        while True:
            try:
                if not self.socket: break
                #=>get a data with parameters as json
                chunk_size = self.config.getInteger('chunk_size',1024)
                data = KDFSProtocol.receiveMessage(self.socket,chunk_size,self.isPacketFile,self.isBinaryFile)
                # check if data is empty
                # if data is None:
                #     continue
                # increase packet number
                self.packetNumber += 1
                # get data as command
                if self.packetNumber == 1:
                    command = data
                    self.commandData = command
                    # if next packet is file
                    if command['send_file']: self.isPacketFile = True
                    # if next packet is binary file
                    if command['send_binary']: self.isBinaryFile = True
                else:
                    command = self.commandData
                    self.commandData = ''
                # check for empty command
                if command == '':
                    print("(server) No command received. shutting down socket...")
                    self.socket.close()
                    break
                print('(server) Command Request received : {} (request #{})'.format(command['command'],self.packetNumber))
                response = ''
                # get queen command response as json
                if command['send_by'] == 'queen':
                    response = self.getQueenCommandResponse(command['command'],command['params'],data,self.packetNumber)
                    print("(server) Sending response for {} node...".format(command['send_by']))
                    
                # get client command response as json (for queen!)
                elif self.config.getBoolean('is_queen',False):
                    response = self.getClientCommandResponse(command['command'],command['params'])
                    print("(queen) Sending response for {} node...".format(command['send_by']))
                    # print("(debug) response:",response)
                # send response of command
                KDFSProtocol.sendMessage(self.socket,chunk_size,response)
                
                
            except Exception as e:
                print("(server) connection closed by client.(1)",e)
                # raise
                break
    # -----------------------------------
    def getClientCommandResponse(self,command : str,params:list=[]):
        from commands.list import listCommand
        # list command
        if command == 'list':
            return listCommand(params).response()

        # any other invalid commands
        else:
            return KDFSProtocol.sendResponseFormatter('',['Not found such command from client!'])
    # -----------------------------------
    def getQueenCommandResponse(self,command:str,params:dict={},data=None,packnumber=1):
        response = ''
        error = ''
        # identify command
        if command == 'identify':
            response = MinimalCommands.identifyCommand()
        # upgrade command
        elif command == 'upgrade':
            response = MinimalCommands.upgradeCommand(params['version'],data,packnumber)
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