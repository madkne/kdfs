
from commands.base import baseCommand
from server.ServerUtils import ServerUtils

import os
import uuid
import platform
import json

class listCommand(baseCommand):
    _CommandParamsNames = ['path']
    _CommandResponseType = 'table'
    _CommandPermissions = ['r']
    # ------------------------------
    def __init__(self,ip,params:list):
        super().__init__(ip,'list',params)
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
        # check for command permission
        if not self._IsAccessToCommand: return super().response(res,err)
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
            # get response by path
            response = self._getNodeIPsByPath()
            # if raise an error
            if response['error'] is not None:
                return super().response(res,[response['error']])
            else: response = response['data']
            # print("(debug) list full response:",response)
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
