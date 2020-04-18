
from server.KDFSProtocol import KDFSProtocol

import json
import socket
from time import gmtime, strftime

class KDFSQueen:
    GLOBAL_PORT = 4040
    GLOBAL_CHUNK_SIZE = 1024
    GLOBAL_NODES_PATH = 'nodes.json'

    def __init__(self,port,start_ip:str,end_ip:str,chunk_size=1024):
        self.GLOBAL_PORT = port
        self.GLOBAL_CHUNK_SIZE = chunk_size
        # scan all up hosts and validate kdfs node
        self.validateNodes(start_ip,end_ip)

    # ----------------------------------
    def validateNodes(self,start:str,end:str):
        print(f"(queen) validating all KDFS nodes from {start} to {end}...")
        # parse start ip
        start_c = int(start.split('.')[2])
        end_c = int(end.split('.')[2])
        start_d = int(start.split('.')[3])
        end_d = int(end.split('.')[3])
        min_ij = start_c*1000 + start_d
        max_ij = end_c*1000 + end_d
        # iterate all ip addresses
        for i in range(start_c,end_c+1,1):
            for j in range(0,255,1):
                ij = i*1000 + j
                # check for in range ip addresses
                if ij < min_ij or ij > max_ij: continue
                currentIP = "192.168.{}.{}".format(i,j)
                print("(queen) check for {} : ".format(currentIP),end='\t')
                socketi = self.socketConnect(currentIP,self.GLOBAL_PORT)
                try:
                    # send identify command
                    KDFSProtocol.sendMessage(socketi,self.GLOBAL_CHUNK_SIZE,KDFSProtocol.sendCommandFormatter('identify'))
                    # get response of command, if exist!
                    response = KDFSProtocol.receiveMessage(socketi,self.GLOBAL_CHUNK_SIZE)
                    print("ACCEPT",end='\t')
                    # print ('Received', repr(response))
                    # check for verify node
                    nodeName=self.findNodeByMacAddress(response['macaddr'])
                    if nodeName != None:
                        print("DETECTED [{}]".format(nodeName))
                        # update node info
                        self.updateNodeByName(nodeName,{
                            'ip'            : currentIP,
                            'last_updated'  : strftime("%Y-%m-%d %H:%M:%S", gmtime())
                        })
                    else:
                        print("UNDEFINED")
                    # print('(debug) is valid node:',response['macaddr'],self.findNodeByMacAddress(response['macaddr']))

                except Exception:
                    print("REJECT")
                    # raise
                finally:
                    # close socket 
                    socketi.close()
                    
        print("\n")
    # ----------------------------------
    def findNodeByMacAddress(self, macaddr:str):
        # open nodes.json
        nodes : dict = json.load(open(self.GLOBAL_NODES_PATH,'r'))
        for key,vals in nodes.items():
            if vals['macaddr'] == macaddr:
                return key
        return None
    # ----------------------------------
    def updateNodeByName(self, name:str,values:dict={}):
        # open nodes.json
        nodes : dict = json.load(open(self.GLOBAL_NODES_PATH,'r'))
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
                "arch": values.get('arch',node['arch'])
            }
        })
        # write and update to nodes.json
        json.dump(nodes,open(self.GLOBAL_NODES_PATH,'w'))


    # ----------------------------------
    def socketConnect(self,host:str,port:int):
        socketi = None
        try:
            socketi = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
            # timeout to connect to socket is 1 seconds
            socketi.settimeout(1)                               
            # bind to the port
            socketi.connect((host, port))
        except Exception:
            pass

        return socketi