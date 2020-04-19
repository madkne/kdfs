
from server.KDFSProtocol import KDFSProtocol
from server.ServerUtils import ServerUtils

import json
import socket
from time import gmtime, strftime

class KDFSQueen:
    GLOBAL_PORT = 4040
    GLOBAL_CHUNK_SIZE = 1024
    # ----------------------------------
    def __init__(self,port,start_ip:str,end_ip:str,chunk_size=1024):
        self.GLOBAL_PORT = port
        self.GLOBAL_CHUNK_SIZE = chunk_size
        # scan all up hosts and validate kdfs node
        self.scanNodes(start_ip,end_ip)

    # ----------------------------------
    def scanNodes(self,start:str,end:str):
        print(f"(queen) validating all KDFS nodes from {start} to {end}...")
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

        # print("(debug) ",detected,len(IPpool))
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
        print("(queen) check for {} : ".format(IP),end='\t')
        socketi = ServerUtils.socketConnect(IP,self.GLOBAL_PORT)
        
        try:
            # send identify command
            KDFSProtocol.sendMessage(socketi,self.GLOBAL_CHUNK_SIZE,KDFSProtocol.sendCommandFormatter('identify',{},True))
            # get response of command, if exist!
            response = KDFSProtocol.receiveMessage(socketi,self.GLOBAL_CHUNK_SIZE)['data']
            print("ACCEPT",end='\t')
            state = 'accept'
            # print('(debug) node identify:',response,len(response))
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


    