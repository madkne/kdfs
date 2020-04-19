
from commands.base import baseCommand
from server.ServerUtils import ServerUtils

import os
import uuid
import platform
import json

class listCommand(baseCommand):
    _CommandParamsNames = ['path']
    _CommandResponseType = 'table'
    # ------------------------------
    def __init__(self,params:list):
        super().__init__('list',params)
    # ------------------------------
    def response(self):
        """
            response list contains:
                - name
                - size
                - type (file,dir,pc)
                - path
        """
        res = []
        err = []
        # get list of all nodes as drives, if path is empty
        if self._CommandParams['path'] is None or self._CommandParams['path'] == '.':
            nodes = self._getActiveNodes()
            for key,vals in nodes.items():
                res.append({
                    'name' : key,
                    'size' : '4.0K',
                    'type' : "pc",
                    'path' : "{}://".format(key)
                })
        # if path not empty
        else:
            # parse path
            parsedPath = self._parsePath(self._CommandParams['path'])
            # print("(debug) list:",self._CommandParams,parsedPath)
            # get all selected in path nodes IPs
            nodesIPs = self._getNodesByName(parsedPath['node'])
            # broadcasting list command with params to all selected nodes
            response = self._broadcastCommand(nodesIPs,'list',{'path':parsedPath['rel_path']})
            print("(debug) list full response:",response)
            # normalize response 
            for name,resp in response.items():
                # resp = json.loads(resp)
                if resp is None or resp['data'] is None:
                    continue
                # check for any errors
                if len(resp['errors']) > 0:
                    err.append(resp['errors'][0])
                # get response and append to res
                else:
                    for item in resp['data']:
                        res.append({
                            'name' : item['name'],
                            'size' : item['size'],
                            'type' : item['type'],
                            'path' : "{}://{}".format(name,item['path'])
                        })


        # res.append({'ffff':self._CommandParams['path']})
        # res : dict = {
        #     'macaddr' : self.getMacAddress(),
        #     'version' : self._getConfig().getInteger('version'),
        #     'os'      : platform.system(),
        #     'arch'    : platform.machine(),
        #     'hostname': platform.node(),
        #     'node_type': 'queen' if self._getConfig().getBoolean('is_queen',False) else 'node'
        # }
        return super().response(res,err)
    # ------------------------------
    @staticmethod
    def getMacAddress():
        macaddr = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) 
for ele in range(0,8*6,8)][::-1])
        return macaddr
    # ------------------------------
    # ------------------------------
    # ------------------------------
