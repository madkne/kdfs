from server.ServerUtils import ServerUtils
from libs.Config import Config

import os
import platform

class MinimalCommands:
    CONFIG_PATH = 'kdfs.conf'
    # ------------------------------------------------
    @staticmethod
    def listCommand(pathi:str,storage_path:str):
        response = []
        # create absolute path with storage path
        absPath = os.path.abspath("{}/{}".format(storage_path,pathi))
        # check for exist directory
        if not os.path.exists(absPath) or not os.path.isdir(absPath):
            return "no such directory to retrive"
        # get list of files and dirs
        files = os.listdir(absPath)
        # iterate all files
        for filei in files:
            newPath = os.path.join(absPath,filei)
            sizei = os.stat(newPath).st_size
            # translate size humanly
            units = ['K','M','G','T']
            size = f"{sizei}B"
            for unit in units:
                if sizei > 1000:
                    sizei /= 1000
                    size = f"{sizei:.1f}{unit}"
            
            # append to response
            response.append({
                'name' : filei,
                'size' : size,
                'type' : 'dir' if os.path.isdir(newPath) else 'file',
                'path' : os.path.join(pathi,filei)
            })

        return response
    # ------------------------------------------------
    @staticmethod
    def identifyCommand():
        # get kdfs config
        config = Config(MinimalCommands.CONFIG_PATH)
        res : dict = {
            'macaddr' : ServerUtils.getMacAddress(),
            'version' : config.getInteger('version',0),
            'os'      : platform.system(),
            'arch'    : platform.machine(),
            'hostname': platform.node(),
            'node_type': 'queen' if config.getBoolean('is_queen',False) else 'node'
        }
        return res