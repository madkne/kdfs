
from commands.base import baseCommand
from server.ServerUtils import ServerUtils

import os
import uuid
import platform
import pwd
import json

class existCommand(baseCommand):
    _CommandParamsNames = ['path']
    _CommandResponseType = 'text'
    _CommandPermissions = ['r']
    # ------------------------------
    def __init__(self,ip,params:list):
        super().__init__(ip,'exist',params)
    # ------------------------------
    def response(self):
        """
            response exist contains:
                true | false
        """
        res = ''
        err = []
        # check for command permission
        if not self._IsAccessToCommand: return super().response(res,err)
        # get response by path
        response = self._getNodeIPsByPath(just_one_node=True)
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
                res = resp['data']

            # print("(debug) stat:",res,err)

        return super().response(res,err)
    # ------------------------------
    # ------------------------------
    # ------------------------------
    # ------------------------------
