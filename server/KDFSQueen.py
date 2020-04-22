
from server.KDFSProtocol import KDFSProtocol
from server.ServerUtils import ServerUtils
from libs.Config import Config

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
        # if not detect all nodes by them old IPs
        if detected < len(IPpool):
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
        socketi = ServerUtils.socketConnect(IP,self.GLOBAL_PORT,2)
        
        try:
            # send identify command
            KDFSProtocol.sendMessage(socketi,self.GLOBAL_CHUNK_SIZE,KDFSProtocol.sendCommandFormatter('identify',{},True))
            # get response of command, if exist!
            response = KDFSProtocol.receiveMessage(socketi,self.GLOBAL_CHUNK_SIZE)['data']
            print("ACCEPT",end='\t')
            state = 'accept'
            # print('(debug) node identify:',response)
            # check for verify node
            nodeName=ServerUtils.findNodeByMacAddress(response['macaddr'])
            if nodeName != None:
                print("DETECTED [{}]".format(nodeName))
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

        except Exception as e:
            print("REJECT")
            # raise
            state = 'reject'
            # raise
        finally:
            # close socket 
            if socketi is not None:
                socketi.close()
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
                "upgrade.sh"
            ]
            with tarfile.open(zip_path, 'w:gz') as kdfsTar:
                for f in files:   
                    kdfsTar.add(f)

        # connect to node and send upgrade file for it
        socketi = ServerUtils.socketConnect(ip,self.GLOBAL_PORT,self.GLOBAL_CONFIG.getInteger('max_timeout',60))
        try:
            # send upgrade command
            KDFSProtocol.sendMessage(socketi,self.GLOBAL_CHUNK_SIZE,KDFSProtocol.sendCommandFormatter('upgrade',{'version':version},True,True,True,send_once=False))
            # get response of command, if exist!
            response = KDFSProtocol.receiveMessage(socketi,self.GLOBAL_CHUNK_SIZE)['data']
            # if response not 'yes', then failed upgrading!
            if response != 'yes':
                KDFSProtocol.echo("Failed upgrading by node server",'queen',response)
                return False
            # KDFSProtocol.echo('(debug) node upgrade:',response,len(response))
            # read new kdfs zip file
            filecontent = b''
            with open(zip_path, mode='rb') as f:
                filecontent = f.read()
            # send new kdfs zip file to node 
            # KDFSProtocol.echo("(debug) filcontent:",filecontent)
            KDFSProtocol.sendMessage(socketi,self.GLOBAL_CHUNK_SIZE,filecontent,True,True)
            # get response for success upgrading or failed!
            response = KDFSProtocol.receiveMessage(socketi,self.GLOBAL_CHUNK_SIZE)['data']

            if response == 'success':
                KDFSProtocol.echo("Success upgrading of \"{}\" node server! Reconnect later (about 3 sec later)".format(name),'queen')
            else:
                KDFSProtocol.echo("Seems that Failed upgrading of \"{}\" node server".format(name,),'queen',response)

            # close connection
            socketi.close()


        except (Exception,KeyboardInterrupt) as e:
            KDFSProtocol.echo("Failed upgrading by Exception",'queen',e)
            return False
            # raise
        finally:
            # close socket 
            if socketi is not None:
                socketi.close()


    