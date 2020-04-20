
from libs.Config import Config
from server.ServerUtils import ServerUtils
from server.KDFSProtocol import KDFSProtocol

import json
import os


class baseCommand:
    _KDFSConfig : Config = None
    _CommandParams : dict = {}
    _CommandParamsNames : list = []
    _CommandResponseType = 'text' #array,table
    # ------------------------------
    def __init__(self,commandName:str,params:list=[]):
        # map params by command params names
        for i in range(0,len(self._CommandParamsNames),1):
            if i < len(params):
                self._CommandParams[self._CommandParamsNames[i]] = params[i]
            else:
                self._CommandParams[self._CommandParamsNames[i]] = None

    # ------------------------------
    def response(self,res,err,just_data=False):
        if just_data: return json.dumps(res)
        
        return KDFSProtocol.sendResponseFormatter(res,err,{
            'type' : self._CommandResponseType
        })
    # ------------------------------
    def _getConfig(self):
        # read kdfs config file
        if self._KDFSConfig is None:
            self._KDFSConfig = Config(ServerUtils.CONFIG_PATH)
        return self._KDFSConfig
    # ------------------------------
    def _getActiveNodes(self):
        return ServerUtils.getAllNodes(True)
    # ------------------------------
    def _parsePath(self,pathi:str):
        # if lpathi.split('://')
        # pathi+=' '
        resPath = {'node':None,'rel_path':pathi}
        # split path with '://'
        sp = pathi.split('://')
        if len(sp) == 2:
            # get node name
            resPath['node'] = sp[0].strip()
            # get node relative path
            resPath['rel_path'] = sp[1].strip()

        return resPath
    # ------------------------------
    def  _getNodesByName(self,node_name:str='*'):
        nodesIPs = []
        # get all actived nodes
        nodes = self._getActiveNodes()
        # iterate all nodes
        for key,vals in nodes.items():
            # if all nodes selected
            if node_name == '*':
                nodesIPs.append(vals['ip'])
            # if just one node selected
            elif key == node_name:
                nodesIPs.append(vals['ip'])

        return nodesIPs
    # ------------------------------
    def _broadcastCommand(self,nodesIPs:list,command,params:dict={}):
        # get kdfs config
        finalResponse = {}
        config = self._getConfig()
        port = config.getInteger('queen_port',4040)
        chunk_size = config.getInteger('chunk_size',1024)
        # iterate all selected nodes
        for IP in nodesIPs:
            # get node name by IP
            nodeName = ServerUtils.findNodeByIP(IP)
            print("(command) sending \"{}\" command by \"{}\" param(s) to \"{}\" node ...".format(command,','.join(params),nodeName))
            socketi = ServerUtils.socketConnect(IP,port)
            try:
                # send list command with relative path
                KDFSProtocol.sendMessage(socketi,chunk_size,KDFSProtocol.sendCommandFormatter(command,params,True))
                # get response of command, if exist!
                response = KDFSProtocol.receiveMessage(socketi,chunk_size)
                # print('(debug) node list response:',response)
                # append response to final by node name
                finalResponse[nodeName] = response


            except Exception as e:
                pass
            finally:
                # close socket 
                if socketi is not None:
                    socketi.close()

        return finalResponse
    # ------------------------------
    # ------------------------------
    # ------------------------------