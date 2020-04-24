
#*****************************************
from libs.Config import Config
from libs.termcolor import cprint
from libs.tabulate import tabulate
from server.KDFSProtocol import KDFSProtocol
from server.ServerUtils import ServerUtils

import os.path
import sys
import time
import io
import math
import socket
import time
import platform
# ------------------------------------------------
KDFSConfig : Config
# ------------------------------------------------
def raiseError(err,isClientError=False):
    if isClientError:
        cprint('\r>> [ERR] '+err,'red',attrs=['bold'],file=sys.stderr)
    else:    
        cprint(err,'red',attrs=['bold'],file=sys.stderr)
# ------------------------------------------------
def help():
    print("Welcome to Kimia Kimia Distributed File System {}!  This is the help utility.".format(KDFSConfig.get('version','unknown')))
    # if exist help file
    if os.path.exists('./KDFSHelp'):
        with open('./KDFSHelp','r') as f:
            print()
            helpText = f.readlines()
            for line in helpText:
                line = line.strip()
                if len(line) == 0: continue
                if line[0] == '-':
                    cprint(line,'cyan')
                elif line.startswith('>'):
                    cprint('\t'+line,'white',attrs=['bold'])
                else:
                    print(line)
            print()
    # if not exist help file
    else:
        raiseError("Not Found Help Document of KDFS Client!",False)
# ------------------------------------------------
def displayResponseAsTable(response: list):
    itemsList = []
    headers = []
    if len(response) == 0:
        return
        
    # get headers of response
    for key,val in response[0].items():
        headers.append(key)
    # get items list of response
    for item in response:
        itemi = []
        for key,val in item.items():
            itemi.append(val)
        itemsList.append(itemi)
        #     print(val,end=lastSpaces)
        # print()
    print(tabulate(itemsList, headers=headers, tablefmt='orgtbl'))

# ------------------------------------------------
def displayResponseAsArray(response: dict):
    itemsList = []
    # get items list of response
    for key in response:
        itemsList.append([key,response[key]])
        #     print(val,end=lastSpaces)
        # print()
    print(tabulate(itemsList, tablefmt='presto'))

# ------------------------------------------------
currentMilliseconds = lambda: int(round(time.time() * 1000))
# ------------------------------------------------
# when start kdfs client program
if __name__ == "__main__":
    # read kdfs config file
    KDFSConfig = Config(ServerUtils.CONFIG_PATH)
    # KDFSConfig.read("kdfs.conf")
    cprint("KDFS CLIENT shell (version {})".format(KDFSConfig.get('version','unknown')),'blue',attrs=['bold'])
    print("Using \"help\" for more information.")
    print("\n")
    # if not found any command
    if len(sys.argv) <= 1:
        help()
        exit(0)
    # get user command
    command = sys.argv[1]
    params = sys.argv[2:]
    # print('argvs:',command,params)
    # check for arguments
    if command == 'help':
        help()
    else:
        # start time of process command
        startTime = currentMilliseconds()
        # set loading
        print('Please Wait...',end="\r")
        try:
            # create a socket object
            socketi = ServerUtils.socketConnect(KDFSConfig.get('client_ip','127.0.0.1'),KDFSConfig.getInteger('client_port',4041),KDFSConfig.getInteger('max_timeout',60))
            # send command to server
            chunk_size = KDFSConfig.getInteger('chunk_size',1024)
            KDFSProtocol.sendMessage(socketi,chunk_size,KDFSProtocol.sendCommandFormatter(command,params))
            # print("(debug):",socketi,chunk_size,command,params)
            # get response of command
            response = KDFSProtocol.receiveMessage(socketi,chunk_size)
            # print("(debug) receive response : ",response)
            # end time of process command
            endTime = currentMilliseconds()
            # show command with params on output
            print("\r({}) >> [{} sec] {} {}\n\n".format(platform.node(),(endTime-startTime)/1000, command,' '.join(params)))
            # check for errors
            if response is None or response['data'] is None:
                raiseError("Can not retrive response from server!",True)
                exit(1)
            if len(response['errors']) > 0:
                for err in response['errors']:
                    raiseError(err,True)
                exit(1)
            # get response type from meta
            responseType = response['meta']['type']
            # if response type is table
            if responseType == 'table':
                displayResponseAsTable(response['data'])
            # if response type is array
            elif responseType == 'array':
                displayResponseAsArray(response['data'])
            # if response type is text
            elif responseType == 'text':
                print(response['data'])
            # close socket
            socketi.close()
        except KeyboardInterrupt:
            exit(0)
        except Exception as e:
            raiseError("can not connect to local kdfs server or retrive response :{}".format(e),False)
            raise
            # print("raise an exception:",e)
            exit(1)
        finally:
            print()