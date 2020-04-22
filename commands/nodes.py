
from commands.base import baseCommand
from server.ServerUtils import ServerUtils
from server.KDFSProtocol import KDFSProtocol

import os
import uuid
import platform
import pwd
import json
from time import gmtime, strftime

class nodesCommand(baseCommand):
    _CommandParamsNames = ['mode','name','property','value']
    _CommandResponseType = 'text'
    _CommandPermissions = ['s']
    # ------------------------------
    def __init__(self,ip,params:list):
        super().__init__(ip,'nodes',params)
    # ------------------------------
    def response(self):
        """
            response nodes contains:
                - nodes add
                    - ip
                    - mac_address
                    - os
                    - hostname
                - nodes add [name] [ip]
                    - success | false
        """
        res = ''
        err = []
        # check for command permission
        if not self._IsAccessToCommand: return super().response(res,err)
        # check for nodes mode
        if self._CommandParams['mode'] == 'add':
            (res,errori) = self.nodesAdd(self._CommandParams['name'],self._CommandParams['property'])
        
        # if raise an error
        if errori is not '':
            return super().response(res,[errori])

        # print("(debug) list full response:",res)

            # print("(debug) stat:",res,err)

        return super().response(res,err)
    # ------------------------------
    def nodesAdd(self, name=None,ip=None):
        # print('nodes add:',name,ip)
        # if node name and ip address is empty, then return list of scan nodes
        if name is None :
            # change command response type
            self._CommandResponseType = 'table'
            undefinedNodes = []
            # get all IP addresses between start and end IPs
            IPpool = ServerUtils.getIPAddressesPool(self._getConfig().get('nodes_start_ip','192.168.1.0'),self._getConfig().get('nodes_end_ip','192.168.1.255'))
            # iterate all ip addresses in pool
            for IP in IPpool:
                response = ServerUtils.sendAndReceiveServerIdentify(self._getConfig(),IP)
                if response == None: continue
                # check for verify node
                nodeName=ServerUtils.findNodeByMacAddress(response['macaddr'])
                if nodeName == None:
                    undefinedNodes.append({
                        'ip' : IP,
                        'mac_address' : response['macaddr'],
                        'os' : response['os'],
                        'hostname': response['hostname']
                    })
            # return undefined nodes list
            return (undefinedNodes,'')

        # if exist ip and node name, check it and add it to nodes database
        elif name is not None and ip is not None:
            response = ServerUtils.sendAndReceiveServerIdentify(self._getConfig(),ip)
            # check for valid node by ip in local network
            if response == None: return ('','can not find such node by \"{}\"'.format(ip))
            # check for not duplicate node name
            if ServerUtils.getNodeByName(name) is not None:
                return ('','such node by \"\" name is exist'.format(name))
            # open nodes.json
            nodes : dict = json.load(open(ServerUtils.GLOBAL_NODES_PATH,'r'))
            # add new node to nodes database
            nodes[name] = {
                "macaddr": response['macaddr'],
                "version": response['version'], 
                "os": response['os'], 
                "ip": ip,
                "last_updated": strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                "perms": 'b',
                "arch": response['arch'],
                "hostname": response['hostname'],
                "node_type": response['node_type'],
                "state":"on"
            }
            # write and update to nodes.json
            json.dump(nodes,open(ServerUtils.GLOBAL_NODES_PATH,'w'))
            
            return ('success to adding node in database','')
            


    # ------------------------------
    # ------------------------------
    # ------------------------------
