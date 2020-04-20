
#*****************************************
from libs.Config import Config
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
def help():
    print("Welcome to Kimia Kimia Distributed File System {}!  This is the help utility.".format(KDFSConfig.get('version','unknown')))
    print("\
        - list [path]\
        \nreturn list of directories and files in [path] (perm:r)\
        \n\t> list\
        \n\t> list pc1://home\
        ---------------------------\n\
        - info [mode=file] [path]\
        \nreturn info of file in [path] (perm:r+)\
        \n\t> info file pc1://hello.md\
        ---------------------------\n\
        ")
# ------------------------------------------------
def displayResponseAsTable(response: list):
    lastSpaces = '  '
    itemsList = []
    headers = []
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
currentMilliseconds = lambda: int(round(time.time() * 1000))
# ------------------------------------------------
# when start kdfs client program
if __name__ == "__main__":
    # read kdfs config file
    KDFSConfig = Config(ServerUtils.CONFIG_PATH)
    # KDFSConfig.read("kdfs.conf")
    print("KDFS CLIENT shell (version {})".format(KDFSConfig.get('version','unknown')))
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
            socketi = ServerUtils.socketConnect(KDFSConfig.get('client_ip','127.0.0.1'),KDFSConfig.getInteger('client_port',4041),60)
            # send command to server
            chunk_size = KDFSConfig.getInteger('chunk_size',1024)
            KDFSProtocol.sendMessage(socketi,chunk_size,KDFSProtocol.sendCommandFormatter(command,params))
            # get response of command
            response = KDFSProtocol.receiveMessage(socketi,chunk_size)
            # print("(debug) receive response : ",response)
            # end time of process command
            endTime = currentMilliseconds()
            # show command with params on output
            print("({}) >> [{} sec] {} {}\n\n".format(platform.node(),(endTime-startTime)/1000, command,' '.join(params)))
            # check for errors
            if len(response['errors']) > 0:
                for err in response['errors']:
                    print(">> [ERR]",err)
                exit(1)
            # get response type from meta
            responseType = response['meta']['type']
            # if response type is table
            if responseType == 'table':
                displayResponseAsTable(response['data'])
            # close socket
            socketi.close()
        except KeyboardInterrupt:
            exit(0)
        except Exception as e:
            print("can not connect to local kdfs server or retrive response!",e)
            # raise
            # print("raise an exception:",e)
            exit(1)
        finally:
            print()