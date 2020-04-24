
from libs.Config import Config
from server.ServerUtils import ServerUtils
from server.KDFSProtocol import KDFSProtocol

import json
import os


class baseCommand:
    _KDFSConfig : Config = None
    _CommandParams : dict = {}
    _CommandName : str = ''
    _CommandParamsNames : list = []
    _CommandResponseType = 'text' #array,table
    _CommandPermissions : list = []
    _IsAccessToCommand = True
    # ------------------------------
    def __init__(self,ip:str,commandName:str,params:list=[]):
        # set command name as global
        self._CommandName = commandName
        # check permissions of command by permissions of client
        if len(self._CommandPermissions) > 0:
            nodename = ServerUtils.findNodeByIP(ip)
            nodePerms = ServerUtils.getNodePermssionsByName(nodename)
            # KDFSProtocol.echo((ip,nodename,nodePerms),'debug')
            is_exist = True
            for perm in self._CommandPermissions:
                exist = False
                for nodeperm in nodePerms:
                    if nodeperm == perm:
                        exist = True
                        break
                if not exist: 
                    is_exist = False
                    break
            # if client not permmitted
            if not is_exist:
                self._IsAccessToCommand = False
        # map params by command params names
        for i in range(0,len(self._CommandParamsNames),1):
            if i < len(params):
                self._CommandParams[self._CommandParamsNames[i]] = params[i]
            else:
                self._CommandParams[self._CommandParamsNames[i]] = None

    # ------------------------------
    def response(self,res,err=[],just_data=False):
        # check for command permission
        if not self._IsAccessToCommand:
            res = ''
            err = ['Permission denied']

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
    def _getNodeIPsByPath(self,just_one_node=False,is_broadcast=True,params={}):
        # parse path
        parsedPath = self._parsePath(self._CommandParams['path'])
        # print("(debug) list:",self._CommandParams,parsedPath)
        # get all selected in path nodes IPs
        nodesIPs = self._getNodesByName(parsedPath['node'])
        # print("node ips:",nodesIPs)
        # if more than 1 nodes selected
        if just_one_node and len(nodesIPs) > 1:
            return {'data':None,'error':"stat command can not retrive for multiple nodes"}
        elif len(nodesIPs) == 0:
            return {'data':None,'error':"not Found any node by path"}
        # if not broadcasting and stop it!
        if not is_broadcast: 
            return {"data":{'ips':nodesIPs,'rel_path':parsedPath['rel_path']},"error":None}
        # append rel path to params
        params['path'] = parsedPath['rel_path']
        # broadcasting stat command with params to all selected nodes
        response = self._broadcastCommand(nodesIPs,self._CommandName,params)

        return {'data':response,'error':None}
        
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
    def  _getNodesByName(self,node_name:str='*') -> list:
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
    def _broadcastFile(self,nodeIPs:list,command,params:dict={},file_content=b''):
        # get kdfs config
        finalResponse = {}
        config = self._getConfig()
        port = config.getInteger('queen_port',4040)
        chunk_size = config.getInteger('chunk_size',1024)
        socket_list = {}
        # create socket connections by IP nodes
        for IP in nodeIPs:
            # get node name by IP
            nodeName = ServerUtils.findNodeByIP(IP)
            # connect to socket server
            socketi = ServerUtils.socketConnect(IP,port,config.getInteger('max_timeout',60))
            try:   
                # send command with params
                KDFSProtocol.echo("Sending \"{}\" command by \"{}\" param(s) to \"{}\" node ...".format(command,','.join(params),nodeName),'command')

                KDFSProtocol.sendMessage(socketi,chunk_size,KDFSProtocol.sendCommandFormatter(command,params,send_queen=True,send_file=True,max_send_packets=2))
                # get response of command, if exist!
                response = KDFSProtocol.receiveMessage(socketi,chunk_size)
                # KDFSProtocol.echo(f'response data(accept):{response}','debug')
                # get error of response,if exist
                if response['data'] is None or (response['data'] != 'success' and response['data'] != 'yes'):
                    return ('','failed to retrive accept response for send file')
                
                # if file to send, send file
                KDFSProtocol.echo("Sending file for \"{}\" command to \"{}\" node ...".format(command,nodeName),'command')

                # KDFSProtocol.echo(f'data file:{params}','debug')
                KDFSProtocol.sendMessage(socketi,chunk_size,file_content,send_file=True) 
                # get response of file, if exist!
                response = KDFSProtocol.receiveMessage(socketi,chunk_size)
                # get error of response,if exist
                if response['errors'] is not None and len(response['errors'])>1:
                    return ('',response['errors'][0])
                

            except Exception as e:
                KDFSProtocol.echo("Raise an exception when broadcasting file",'command',err=e,is_err=True)
                # raise
            finally:
                # close socket 
                if socketi is not None:
                    socketi.close()
        # return success response to send file successfully
        return ('success','')
    # ------------------------------
    def _broadcastCommand(self,nodesIPs:list,command,params:dict={},recv_file=False):
        # get kdfs config
        finalResponse = {}
        config = self._getConfig()
        port = config.getInteger('queen_port',4040)
        chunk_size = config.getInteger('chunk_size',1024)
        # iterate all selected nodes
        for IP in nodesIPs:
            # get node name by IP
            nodeName = ServerUtils.findNodeByIP(IP)
            KDFSProtocol.echo("Sending \"{}\" command by \"{}\" param(s) to \"{}\" node ...".format(command,','.join(params),nodeName),'command')
            # connect to socket server
            socketi = ServerUtils.socketConnect(IP,port,config.getInteger('max_timeout',60))
            try: 
                # send command with params
                KDFSProtocol.sendMessage(socketi,chunk_size,KDFSProtocol.sendCommandFormatter(command,params,send_queen=True,recv_file=recv_file))
                # get response of command, if exist!
                response = KDFSProtocol.receiveMessage(socketi,chunk_size,is_file=recv_file)
                # print('(debug) node list response:',response)
                # append response to final by node name
                finalResponse[nodeName] = response


            except Exception as e:
                KDFSProtocol.echo("Raise an exception when broadcasting command",'command',err=e,is_err=True)
                # raise
            finally:
                # close socket 
                if socketi is not None:
                    socketi.close()

        return finalResponse
    # ------------------------------
    # ------------------------------
    # ------------------------------