
from commands.base import baseCommand
from server.ServerUtils import ServerUtils

import os
import uuid
import platform
import json

class notifyCommand(baseCommand):
    _CommandParamsNames = ['text']
    _CommandResponseType = 'text'
    _CommandPermissions = ['s']
    # ------------------------------
    def __init__(self,ip,params:list):
        super().__init__(ip,'notify',params)
    # ------------------------------
    def response(self):
        """
            response list contains:
                - send notification to 3 nodes
        """
        # check for command permission
        if not self._IsAccessToCommand: return super().response('',[])
        # get all nodes IPs
        nodesIPs = self._getNodesByName('*')
        # broadcasting list command with params to all selected nodes
        response = self._broadcastCommand(nodesIPs,'notify',{'text':self._CommandParams['text']})
        # print("(debug) list full response:",response)
        success_notifies = 0
        # iterate all response and count success responses
        for resp in response:
            if resp['data'] == 'success':
                success_notifies += 1
        
        return super().response('send notification to {} nodes and got {} success responses'.format(len(nodesIPs), success_notifies))
            
    # ------------------------------
    # ------------------------------
    # ------------------------------
    # ------------------------------
