
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
def help():
    print("Welcome to Kimia Kimia Distributed File System {}!  This is the help utility.".format(KDFSConfig.get('version','unknown')))
    print("\
        \nlist [path]\
        \nreturn list of directories and files in [path] (perm:r)\
        \n\t> list\
        \n\t> list pc1://home\
        \n---------------------------\
        \n- notify [text]\
        \nsend and show a notify text to all nodes of kdfs (perm:s)\
        \n\t> notify \"hello world!\"\
        \n---------------------------\
        \n- stat [path]\
        \nreturn info of file or directory in [path] (perm:r+)\
        \n\t> stat pc1://hello.md\
        \n---------------------------\
        \n- exist [path]\
        \nreturn boolean for check exist path (perm:r)\
        \n\t> exist pc1://foo\
        \n---------------------------\
        \n- find [mode=name|content] [type=rec|file] [path] [regex]\
        \nfind by text (include simple regular expression) in filenames, direnames and contents and return list of find paths (perm:c)\
        \n\t> find name file \"*://\" \"sam%-###.txt\"\
        \n\t> find content all \"pc1://home/\" \"hello world!\"\
        \n---------------------------\
        \n- nodes add [name?] [ip?]\
        \nscan all undefined nodes on local network and user can select one to add in nodes database (perm:s)\
        \n\t> nodes add\
        \n\t> nodes add pc4 \"192.168.1.6\" \
        \n")
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
                cprint(">> [ERR] Can not retrive response from server!",'red',attrs=['bold'])
                exit(1)
            if len(response['errors']) > 0:
                for err in response['errors']:
                    cprint(">> [ERR] {}".format(err),'red',attrs=['bold'])
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
            cprint("can not connect to local kdfs server or retrive response :{}".format(e),'red',attrs=['bold'])
            raise
            # print("raise an exception:",e)
            exit(1)
        finally:
            print()