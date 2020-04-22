
from commands.base import baseCommand
from server.ServerUtils import ServerUtils

import os
import uuid
import platform
import json

class findCommand(baseCommand):
    _CommandParamsNames = ['mode','type','path','regex']
    _CommandResponseType = 'table'
    _CommandPermissions = ['c','r']
    # ------------------------------
    def __init__(self,ip,params:list):
        super().__init__(ip,'find',params)
    # ------------------------------
    def response(self):
        """
            response find contains:
                - name
                - type (file,dir,pc)
                - count
                - path
        """
        res = []
        err = []
        maxItems = self._getConfig().getInteger('list_limit',10)
        countItems = 0
        # check for command permission
        if not self._IsAccessToCommand: return super().response(res,err)
        # get response by path
        response = self._getNodeIPsByPath(params={'mode':self._CommandParams['mode'],'type':self._CommandParams['type'],'regex':self._CommandParams['regex']})
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
                    countItems += 1
                    if len(res) > maxItems: continue
                    res.append({
                        '#'    : countItems,
                        'name' : item['name'],
                        'type' : item['type'],
                        'count': item['count'],
                        'path' : "{}://{}".format(name,item['path'])
                    })

        # print("response:",res,err)

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
