from server.ServerUtils import ServerUtils
from libs.Config import Config
from libs.Notification import Notification
from server.KDFSProtocol import KDFSProtocol
from commands.minimalUitls import minimalUitls

import os
import platform
import socket
import tarfile
import time
import pwd

class MinimalCommands:

    def __init__(self):
        # get kdfs config
        self.config = Config(ServerUtils.CONFIG_PATH)
        self.storage_path = self.config.get('storage','./')
        
    # ------------------------------------------------
    def _getAbsPath(self,pathi:str):
        return os.path.abspath("{}/{}".format(self.storage_path,pathi))
    # ------------------------------------------------
    def listCommand(self,params:dict):
        response = []
        # create absolute path with storage path
        absPath = self._getAbsPath(params['path'])
        # check for exist directory
        if not os.path.exists(absPath) or not os.path.isdir(absPath):
            return ('',"no such directory to retrive")
        # get list of files and dirs
        files = os.listdir(absPath)
        # iterate all files
        for filei in files:
            newPath = os.path.join(absPath,filei)
            sizei = os.stat(newPath).st_size
            # translate size humanly
            size = minimalUitls.convertBytesToHumanly(sizei)
            # append to response
            response.append({
                'name' : filei,
                'size' : size,
                'type' : 'dir' if os.path.isdir(newPath) else 'file',
                'path' : os.path.join(params['path'],filei)
            })

        return (response,'')

    # ------------------------------------------------
    def findCommand(self,params:dict):
        response = []
        # print("minimal:",params)
        # create absolute path with storage path
        absPath = self._getAbsPath(params['path'])
        # check for exist directory
        if not os.path.exists(absPath) or not os.path.isdir(absPath):
            return ('',"no such directory to retrive")
        # get list of files and dirs (can recursion)
        files = minimalUitls.getAllFilesList(absPath,is_recursion=(params['type'] == 'rec'),just_files=(params['type'] == 'file'))
        # get max items
        maxItems = self.config.getInteger('list_limit',10)
        # print('final files:',files)
        # iterate all files
        for filei in files: 
            # print('file to find:',filei)
            # get abs path
            newPath = os.path.join(absPath,filei)
            findCount = 0
            # if search in filename
            if params['mode'] == 'name':
                # search regex on filename
                findCount = len(minimalUitls.searchTextByRegex(filei,params['regex']))
            elif params['mode'] == 'content':
                # check if directory
                if os.path.isdir(newPath): continue
                # check if file is binary
                if minimalUitls.checkIsBinaryFile(newPath): continue
                # open file and read line by line
                try:
                    with open(newPath,'r',encoding='utf-8') as f:
                        for line in f:
                            # search regex on every line
                            findCount += len(minimalUitls.searchTextByRegex(line,params['regex']))
                except:
                    pass

            # append to response
            if findCount > 0 and len(response) <= maxItems:
                response.append({
                    'name' : filei,
                    'count': findCount,
                    'type' : 'dir' if os.path.isdir(newPath) else 'file',
                    'path' : os.path.join(params['path'],filei)
                })

        # print('response_minimal:',params,response)

        return (response,'')

    # ------------------------------------------------
    def existCommand(self,params:dict):
        # create absolute path with storage path
        absPath = self._getAbsPath(params['path'])
        # check for exist path
        if os.path.exists(absPath) :
            return ("true",'')
        else: 
            return ('false','')
    # ------------------------------------------------
    def statCommand(self,params:dict):
        response = {}
        # create absolute path with storage path
        absPath = self._getAbsPath(params['path'])
        # check for exist directory or file
        if not os.path.exists(absPath):
            return ('',"no such file or directory to retrive")
        # get stat of absolute path
        (mode, ino, dev, nlink, uid, gid, sizei, atime, mtime, ctime) = os.stat(absPath) 
        # fileStat = os.stat(newPath)
        # translate size humanly
        size = minimalUitls.convertBytesToHumanly(sizei)
        
        # append to response
        response = {
            'name' : os.path.basename(absPath),
            'size' : size,
            'type' : 'dir' if os.path.isdir(absPath) else 'file',
            'kdfs_path' : params['path'],
            'local_path' : absPath,
            'last_access' : time.ctime(atime),
            'last_modify' : time.ctime(mtime),
            'owner' : pwd.getpwuid( uid ).pw_name
        }

        return (response,'')
    # ------------------------------------------------
    def identifyCommand(self,params:dict={}):
        res : dict = {
            'macaddr' : ServerUtils.getMacAddress(),
            'version' : self.config.getInteger('version',0),
            'os'      : platform.system(),
            'arch'    : platform.machine(),
            'hostname': platform.node(),
            'node_type': 'queen' if self.config.getBoolean('is_queen',False) else 'node'
        }
        return (res,'')
    # ------------------------------------------------
    def upgradeCommand(self,params:dict):
        # if packet number is 1,then just return 'yes' or 'no'
        if params['packnumber'] == 1:
            # check if server can accept upgrades or not
            if self.config.getBoolean('accept_upgrades',True):
                KDFSProtocol.echo("Accept kdfs version {} upgrading...".format(params['version']),'upgrade')
                # check if upgrades folder is not exsit
                if not os.path.exists(ServerUtils.UPGRADE_PATH):
                    os.makedirs(ServerUtils.UPGRADE_PATH)
                # resturn accept response
                return ('yes','')
            else:
                KDFSProtocol.echo("Refuse any upgrading",'upgrade')
                # return refuse response
                return ('no','')
        # if get file in next packet number, save it
        else:
            try:
                # save to file
                with open(ServerUtils.UPGRADE_ZIP_PATH.format(params['version']), mode='wb') as f:
                    f.write(bytearray(params['data']))
                # extract to min source
                with tarfile.open(ServerUtils.UPGRADE_ZIP_PATH.format(params['version']), 'r:gz') as kdfsTar:
                    kdfsTar.extractall("./")
                # update kdfs version number
                self.config.updateItem('version',params['version'])
                KDFSProtocol.echo("saved kdfs version {} upgraded file in local".format(params['version']),'upgrade')
                # if os is linux, then run bash script
                if platform.system() == 'Linux':
                    os.system("sh ./upgrade.sh &")
                else:
                    pass
                    # TODO:

                return ('success','')

            except Exception as e:
                return (e,'')
    # ------------------------------------------------
    def notifyCommand(self,params:dict):
        response = Notification(self.config.get('app_name','KDFS'),params['text'],30).send()
        if response:
            return ('success','')
        else:
            return ('failed','')
