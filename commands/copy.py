
from commands.base import baseCommand
from server.ServerUtils import ServerUtils
from server.KDFSProtocol import KDFSProtocol

import os
import uuid
import platform
import pwd
import json

class copyCommand(baseCommand):
    _CommandParamsNames = ['src_path','dest_path']
    _CommandResponseType = 'text'
    _CommandPermissions = ['w']
    # ------------------------------
    def __init__(self,ip,params:list):
        super().__init__(ip,'copy',params)
    # ------------------------------
    def response(self):
        """
            response copy contains:
                success | failed
        """
        res = ''
        err = []
        # check for command permission
        if not self._IsAccessToCommand: return super().response(res,err)
        # parse src path
        src_path = self._parsePath(self._CommandParams['src_path'])
        # get all selected in path nodes IPs
        src_IP = self._getNodesByName(src_path['node'])
        # if src ip is more than one!
        if len(src_IP) > 1:
            return super().response(res,['can not copy from multiple nodes'])
        # send 'copy' command to src IP and get file compressed, if exist
        response = self._broadcastCommand(src_IP,self._CommandName,{
            'mode' : 'src',
            'path' : src_path['rel_path']
        },recv_file=True)
        # print('response copy:',response,src_path)
        # if response file is empty
        if response == '' or response is None:
            return super().response('',"no such file or directory to retrive")
        # if response has error
        for key,resp in response.items():
            try:
                error = resp.decode(KDFSProtocol.ENCODING)
                return super().response('',[error])
            except:
                pass

        # get original file content as bytes
        for key,resp in response.items():
            file_content = resp
            break
        # ---------------
        # parse dest path
        dest_path = self._parsePath(self._CommandParams['dest_path'])
        # get all selected in path nodes IPs
        dest_IP = self._getNodesByName(dest_path['node'])
        # send 'copy' command with compressed file to dest IP
        (res,err) = self._broadcastFile(dest_IP,self._CommandName,{
            'mode' : 'dest',
            'path' : dest_path['rel_path'],
        },file_content)
        # print('response copy1:',res,err,file_content)
        # check for success send file to dest path
        if res == 'success':
            return super().response('copy file(s) SuccessFully')
        else:
            return super().response('',err)
    # ------------------------------
    # ------------------------------
    # ------------------------------
    # ------------------------------
