# from commands.identify import identifyCommand
from server.KDFSProtocol import KDFSProtocol

import socket
import json
import uuid

class ServerUtils:
    GLOBAL_NODES_PATH = 'database/nodes.json'
    # ----------------------------------
    @staticmethod
    def socketConnect(host:str,port:int,timeout=1):
        socketi = None
        try:
            socketi = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
            # timeout to connect to socket is 1 seconds
            socketi.settimeout(timeout)                               
            # bind to the port
            socketi.connect((host, port))
        except KeyboardInterrupt:
            exit(0)
        except Exception:
            return None

        return socketi
    # ----------------------------------
    @staticmethod
    def checkQueenByIP(ip:str,port:str,chunk_size=1024) -> bool:
        socketi = ServerUtils.socketConnect(ip,port)
        try:
            # send identify command
            KDFSProtocol.sendMessage(socketi,chunk_size,KDFSProtocol.sendCommandFormatter('identify'))
            # get response of command, if exist!
            response = KDFSProtocol.receiveMessage(socketi,chunk_size)
            # close socket
            socketi.close()
            # check for node type 
            if response['node_type'] == 'queen':
                return True

        except Exception:
            return False
        return False
    # ----------------------------------
    @staticmethod
    def getMacAddress():
        macaddr = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) 
for ele in range(0,8*6,8)][::-1])
        return macaddr
    # ----------------------------------
    @staticmethod
    def getAllOldNodeIPs(exclude_this_node=True):
        NodesIPs = []
        ThisMacAddress = ServerUtils.getMacAddress()
        # open nodes.json
        nodes : dict = json.load(open(ServerUtils.GLOBAL_NODES_PATH,'r'))
        for key,vals in nodes.items():
            # check if mac address of node
            if exclude_this_node and ThisMacAddress == vals['macaddr']:
                continue
            NodesIPs.append(vals['ip'])

        return NodesIPs
    # ----------------------------------
    @staticmethod
    def getAllNodes(just_on=True):
        nodes = {}
        # open nodes.json
        nodes : dict = json.load(open(ServerUtils.GLOBAL_NODES_PATH,'r'))
        for key,vals in nodes.items():
            # check if node state is on
            if just_on and vals['state'] == 'off':
                continue
            nodes[key] = vals
        return nodes
    # ----------------------------------
    @staticmethod
    def getIPAddressesPool(start_ip:str,end_ip:str):
        IPpool = []
        # parse start ip
        start_c = int(start_ip.split('.')[2])
        end_c = int(end_ip.split('.')[2])
        start_d = int(start_ip.split('.')[3])
        end_d = int(end_ip.split('.')[3])
        min_ij = start_c*1000 + start_d
        max_ij = end_c*1000 + end_d
        # iterate all ip addresses
        for i in range(start_c,end_c+1,1):
            for j in range(0,255,1):
                ij = i*1000 + j
                # check for in range ip addresses
                if ij < min_ij or ij > max_ij: continue
                currentIP = "192.168.{}.{}".format(i,j)
                IPpool.append(currentIP)

        return IPpool
    # ----------------------------------
    @staticmethod
    def findNodeByMacAddress(macaddr:str):
        # open nodes.json
        nodes : dict = json.load(open(ServerUtils.GLOBAL_NODES_PATH,'r'))
        for key,vals in nodes.items():
            if vals['macaddr'] == macaddr:
                return key
        return None
    # ----------------------------------
    @staticmethod
    def findNodeByIP(ip:str):
        # open nodes.json
        nodes : dict = json.load(open(ServerUtils.GLOBAL_NODES_PATH,'r'))
        for key,vals in nodes.items():
            if vals['ip'] == ip:
                return key
        return None
    # ----------------------------------
    @staticmethod
    def getNodeByName(name:str):
        # open nodes.json
        nodes : dict = json.load(open(ServerUtils.GLOBAL_NODES_PATH,'r'))
        # get values of node, if exist!
        node = nodes.get(name,None)
        return node
    # ----------------------------------
    @staticmethod
    def updateNodeByName(name:str,values:dict={}):
        # open nodes.json
        nodes : dict = json.load(open(ServerUtils.GLOBAL_NODES_PATH,'r'))
        # get values of node, if exist!
        node = nodes.get(name,None)
        if node is None: return
        # update values of node
        nodes.update({
            name : {
                "macaddr": values.get('macaddr',node['macaddr']),
                "version": values.get('version',node['version']), 
                "os": values.get('os',node['os']), 
                "ip": values.get('ip',node['ip']),
                "last_updated": values.get('last_updated',node['last_updated']),
                "perm": values.get('perm',node['perm']),
                "arch": values.get('arch',node['arch']),
                "hostname": values.get('hostname',node['hostname']),
                "node_type": values.get('node_type',node['node_type']),
                "state": values.get('state',node['state']),
            }
        })
        # write and update to nodes.json
        json.dump(nodes,open(ServerUtils.GLOBAL_NODES_PATH,'w'))
    # ----------------------------------
    @staticmethod
    def checkPortInUse(port:int,host='127.0.0.1'):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex((host, port)) == 0
        except OSError:
            return True