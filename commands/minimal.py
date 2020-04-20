from server.ServerUtils import ServerUtils
from libs.Config import Config

import os
import platform
import socket
import tarfile

class MinimalCommands:
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
        config = Config(ServerUtils.CONFIG_PATH)
        res : dict = {
            'macaddr' : ServerUtils.getMacAddress(),
            'version' : config.getInteger('version',0),
            'os'      : platform.system(),
            'arch'    : platform.machine(),
            'hostname': platform.node(),
            'node_type': 'queen' if config.getBoolean('is_queen',False) else 'node'
        }
        return res
    # ------------------------------------------------
    @staticmethod
    def upgradeCommand(version:str,data,packnumber = 1):
        # if packet number is 1,then just return 'yes' or 'no'
        if packnumber == 1:
            # get kdfs config
            config = Config(ServerUtils.CONFIG_PATH)
            # check if server can accept upgrades or not
            if config.getBoolean('accept_upgrades',True):
                print("(upgrade) Accept kdfs version {} upgrading...".format(version))
                return 'yes'
            else:
                print("(upgrade) Refuse any upgrading")
                return 'no'
        # if get file in next packet number, save it
        else:
            try:
                # save to file
                with open(ServerUtils.UPGRADE_ZIP_PATH.format(version), mode='wb') as f:
                    f.write(bytearray(data))
                # extract to min source
                with tarfile.open(ServerUtils.UPGRADE_ZIP_PATH.format(version), 'r:gz') as kdfsTar:
                    kdfsTar.extractall("./")
                # update kdfs version number
                ServerUtils.updateConfig('version',version)
                print("(upgrade) saved kdfs version {} upgraded file in local".format(version))
                
                os.system("sh ./upgrade.sh &")

                return 'success'

            except Exception as e:
                return e
