
from server.KDFSProtocol import KDFSProtocol
from server.ServerUtils import ServerUtils
from libs.Config import Config
from commands.base import baseCommand

import json
import os
import socket
from time import gmtime, strftime
import tarfile
import gzip

class KDFSQueen:
    GLOBAL_PORT = 4040
    GLOBAL_CHUNK_SIZE = 1024
    GLOBAL_CONFIG : Config 
    # ----------------------------------
    def __init__(self,config:Config):
        self.GLOBAL_PORT = config.getInteger('queen_port',4040)
        self.GLOBAL_CHUNK_SIZE = config.getInteger('chunk_size',1024)
        start_ip = config.get('nodes_start_ip','192.168.0.0')
        end_ip = config.get('nodes_end_ip','192.168.5.255')
        self.GLOBAL_CONFIG = config
        # scan all up hosts and validate kdfs node
        self.scanNodes(start_ip,end_ip)

    # ----------------------------------
    def scanNodes(self,start:str,end:str):
        KDFSProtocol.echo(f"validating all KDFS nodes from {start} to {end}...",'queen')
        # validate old ip addresses of nodes by queen
        IPpool = ServerUtils.getAllOldNodeIPs()
        # iterate all ip addresses in pool
        detected = 0
        for IP in IPpool:
            # find node name by its old IP
            nodeName = ServerUtils.findNodeByIP(IP)
            if self.validateNodeByIP(IP) == 'detect':
                detected +=1
                # update and on state of node
                ServerUtils.updateNodeByName(nodeName,{'state':'on'})
            # if not detected, then off its state
            else:
                ServerUtils.updateNodeByName(nodeName,{'state':'off'})

        # KDFSProtocol.echo("(debug) ",detected,len(IPpool))
        # if not detect all nodes by them old IPs and permmit to scan all nodes
        if detected < len(IPpool) and self.GLOBAL_CONFIG.getBoolean('queen_scan_nodes',True):
            # get all IP addresses between start and end IPs
            IPpool = ServerUtils.getIPAddressesPool(start,end)
            # iterate all ip addresses in pool
            for IP in IPpool:
                self.validateNodeByIP(IP)
                    
        print("\n")
    # ----------------------------------
    def validateNodeByIP(self,IP:str):
        state = 'reject'
        KDFSProtocol.echo("check for {} : ".format(IP),'queen',end='\t')
        response = ServerUtils.sendAndReceiveServerIdentify(self.GLOBAL_CONFIG,IP)
        if response is not None:
            print("ACCEPT",end='\t')
            state = 'accept'
            # print('(debug) node identify:',response)
            # check for verify node
            nodeName=ServerUtils.findNodeByMacAddress(response['macaddr'])
            if nodeName != None:
                print("DETECT [{}]".format(nodeName))
                # update node info
                ServerUtils.updateNodeByName(nodeName,{
                    'ip'            : IP,
                    'last_updated'  : strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                    'hostname'      : response['hostname']
                })
                state = 'detect'
                # check for upgrading node
                if int(response['version']) < self.GLOBAL_CONFIG.getInteger('version',1):
                    self.upgradeNodeServer(nodeName,IP)
            else:
                print("UNDEFINED")
        else:
            print("REJECT")
            state = 'reject'
        # return state of node
        return state

    # ----------------------------------
    def upgradeNodeServer(self,name:str,ip:str):
        version = self.GLOBAL_CONFIG.getInteger('version',1)
        zip_path = ServerUtils.UPGRADE_ZIP_PATH.format(version)
        KDFSProtocol.echo("Upgrading \"{}\" node to verison {}...".format(name,version),'queen')
        # create zip file of all files to need upgrade, if not exist!
        if not os.path.exists(zip_path):
            # list of files that must upgrade for any node
            files = [
                "server/__init__.py",
                "server/KDFSProtocol.py",
                "server/KDFSServer.py",
                "server/ServerUtils.py",
                "server/ClientThread.py",
                "kdfs.py",
                "KDFSHelp",
                "kdfs.conf.sample",
                "server.py",
                "libs/__init__.py",
                "libs/Config.py",
                "libs/Daemon.py",
                "libs/tabulate.py",
                "libs/Notification.py",
                "libs/termcolor.py",
                "commands/__init__.py",
                "commands/minimal.py",
                "commands/minimalUitls.py",
            ]
            # if os is linux, then run bash script
            if ServerUtils.detectOS() == 'linux':
                files.append("upgrade.sh")
                files.append("kdfs_server.sh")
            # TODO:
            # compress all files in tar.gz file
            with tarfile.open(zip_path, 'w:gz') as kdfsTar:
                for f in files:   
                    kdfsTar.add(f)

        # connect to node and send upgrade file for it
        try:
            # read new kdfs zip file
            filecontent = b''
            with open(zip_path, mode='rb') as f:
                filecontent = f.read()
            base = baseCommand(ip,'upgrade',[])
            (response,err) = base._broadcastFile([ip],'upgrade',{'version':version},filecontent)
            if response == 'success':
                KDFSProtocol.echo("Success upgrading of \"{}\" node server! Reconnect later (about 3 sec later)".format(name),'queen')
            else:
                KDFSProtocol.echo("Seems that Failed upgrading of \"{}\" node server".format(name),'queen',err=err)

            return True
        except (Exception,KeyboardInterrupt) as e:
            KDFSProtocol.echo("Failed upgrading by Exception",'queen',e)
            return False
            # raise


    