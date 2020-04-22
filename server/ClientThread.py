
from commands.minimal import MinimalCommands
from server.KDFSProtocol import KDFSProtocol
from server.ServerUtils import ServerUtils
from libs.Config import Config


import socket
import importlib
import threading
import json
import os




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
        self.isReceiveOnce = True
        self.MinimalCommands = MinimalCommands()
        KDFSProtocol.echo(f"New server socket thread started for {ip}",'server')
    # -----------------------------------
    def run(self): 
        # KDFSProtocol.echo("(debug) run client ...")
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
                command = {}
                # get data as command
                if self.packetNumber == 1 and data is not None:
                    command = data
                    self.commandData = command
                    # if next packet is file
                    self.isPacketFile = command['send_file']
                    # if next packet is binary file
                    self.isBinaryFile = command['send_binary']
                    # if continue to send packets
                    self.isReceiveOnce = command['send_once']
                else:
                    command = self.commandData
                    self.commandData = ''
                # check for empty command
                if command == '' or command == {} or (self.isReceiveOnce and self.packetNumber > 1):
                    KDFSProtocol.echo("No command received. shutting down socket for \"{}\"...".format(self.ip),'server')
                    self.socket.close()
                    break
                KDFSProtocol.echo('Command Request received : {} (request #{})'.format(command['command'],self.packetNumber),'server')
                response = ''
                # get queen command response as json
                if command['send_by'] == 'queen':
                    response = self.getQueenCommandResponse(command['command'],command['params'],data,self.packetNumber)
                    KDFSProtocol.echo("Sending response for {} node...".format(command['send_by']),'server')
                    
                # get client command response as json (for queen!)
                elif self.config.getBoolean('is_queen',False):
                    response = self.getClientCommandResponse(command['command'],command['params'],self.ip)
                    KDFSProtocol.echo("Sending response for \"{}\" node...".format(command['send_by']),'queen')
                    # KDFSProtocol.echo("(debug) response:",response)
                # send response of command
                KDFSProtocol.sendMessage(self.socket,chunk_size,response)
                
                
            except Exception as e:
                KDFSProtocol.echo("Connection closed by client.(1)",'server',e)
                # raise
                break
    # -----------------------------------
    def getClientCommandResponse(self,command : str,params:list=[],ip:str=''):
        # init vars
        commandClass = None
        # if command is identify
        if command == 'identify':
            (info,err) = MinimalCommands().identifyCommand()
            return KDFSProtocol.sendResponseFormatter(info)
        # check exist such command
        elif os.path.exists("./commands/{}.py".format(command)):
            commandClass = getattr(importlib.import_module("commands.{}".format(command)), "{}Command".format(command))
            return commandClass(ip,params).response()
        # any other invalid commands
        else:
            return KDFSProtocol.sendResponseFormatter('',['Not found such command from client!'])
    # -----------------------------------
    def getQueenCommandResponse(self,command:str,params:dict={},data=None,packnumber=1):
        response = ''
        error = ''
        # append more data to params of command
        params['data'] = data
        params['packnumber'] = packnumber
        # try to calling command of minimal class
        try:
            (response,error) = getattr(self.MinimalCommands,"{}Command".format(command))(params)
        except (AttributeError):
            error = 'Not found such command!'
        # KDFSProtocol.echo("response:{},error:{}".format(response,error),'debug')
    #    return repsonse with error of command
        return KDFSProtocol.sendResponseFormatter(response,[error])
    # -----------------------------------
    def stop(self):
        self._stop_event.set()
    # -----------------------------------
    def stopped(self):
        return self._stop_event.is_set()