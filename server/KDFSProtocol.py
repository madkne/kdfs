from libs.termcolor import cprint,colored


import socket
import sys
import json
import math
import time
import gzip
import os
import tarfile
from datetime import datetime

class KDFSProtocol:
    END_CHUNK = b'\r!\n'
    END_MESSAGE = b'\r!END!\r--\n'
    ENCODING = 'UTF-8'
    MESSAGE_TYPE = 'JSON'
    COMPRESS_LEVEL = 5

    # -------------------------------------------------
    @staticmethod
    def checkChunkSize(chunk_size : int):
        minSize = 10 + len(KDFSProtocol.END_CHUNK) + len(KDFSProtocol.END_MESSAGE)
        if chunk_size < minSize:
            return minSize
        return chunk_size
    # -------------------------------------------------
    @staticmethod
    def fileCompress(file_path:str):
        from server.ServerUtils import ServerUtils as utils
        # get tmp path
        tmp_path = utils.checkTmpDirectory()
        # generate filename
        filename = os.path.join(tmp_path,"tmp_{}.tar.gz".format(int(round(time.time() * 1000))))
        # compress all files in tar.gz file
        with tarfile.open(filename, 'w:gz') as kdfsTar:
             kdfsTar.add(file_path,arcname=os.path.basename(file_path))
        # open and read compressed file
        filecontent = b''
        with open(filename, mode='rb') as f:
            filecontent = f.read()

        return filecontent
    # -------------------------------------------------
    @staticmethod
    def directoryCompress(dir_path:str):
        from server.ServerUtils import ServerUtils as sutils
        from commands.minimalUitls import minimalUitls as mutils
        # get tmp path
        tmp_path = sutils.checkTmpDirectory()
        # generate filename
        filename = os.path.join(tmp_path,"tmp_{}.tar.gz".format(int(round(time.time() * 1000))))
        # get all files and dirs
        files = mutils.getAllFilesList(dir_path,True)
        # print('files to compress:',files)
        parent_dir = os.path.basename(dir_path)
        # compress all files in tar.gz file
        with tarfile.open(filename, 'w:gz') as kdfsTar:
            for f in files:
                kdfsTar.add(os.path.join(dir_path,f),arcname=os.path.join(parent_dir,f))
        # open and read compressed file
        filecontent = b''
        with open(filename, mode='rb') as f:
            filecontent = f.read()

        return filecontent
    # -------------------------------------------------
    @staticmethod
    def multipleFilesCompress(file_paths:list):
        pass
    # -------------------------------------------------
    @staticmethod
    def saveTempCompressedFile(file_content):
        from server.ServerUtils import ServerUtils as utils
        # get tmp path
        tmp_path = utils.checkTmpDirectory()
        # generate filename
        filename = os.path.join(tmp_path,"tmp_{}.tar.gz".format(int(round(time.time() * 1000))))
        # save file in tmp folder
        with open(filename, mode='wb') as f:
            f.write(bytearray(file_content))
        # return file name of saved file
        return filename
    # -------------------------------------------------
    @staticmethod
    def receiveMessage(socketi : socket.socket,chunk_size : int,is_file=False):
        # check for socket not valid
        if socketi == None: return
        message = None
        data = b''
        line = b''
        extra = b''
        counter = 0
        # check for chunk size
        chunk_size = KDFSProtocol.checkChunkSize(chunk_size)
        # iterate on socket to get complete data
        while True:
            try:
                counter += 1
                chunk = socketi.recv(chunk_size)
                chunk_extra = extra + chunk
                line_end = chunk_extra.find(KDFSProtocol.END_CHUNK)
                # check for empty chunk
                if len(chunk_extra) == 0:
                    break 
                # get line of chunk, if exist
                if line_end != -1:
                    # find all end lines of chunk
                    line_end = 0
                    while True:
                        before_line_end = line_end
                        start_ind = line_end + len(KDFSProtocol.END_CHUNK) if line_end>0 else 0
                        line_end = chunk_extra.find(KDFSProtocol.END_CHUNK,start_ind)
                        if line_end == -1 :
                            line_end = before_line_end
                            break
                        line = line + chunk_extra[start_ind:line_end]
                        data += line
                        line = b''
                    # get extra bytes of chunk for appending to next chunk
                    extra = chunk_extra[line_end+len(KDFSProtocol.END_CHUNK):]
                # if line not completed, wait!
                else:
                    line += chunk_extra
                    extra = b''
                # KDFSProtocol.echo("(debug) chunk:{}\nchunk_extra:{} (extra:{})\nline:{} (line_end:{},chunk_size:{})\ndata:{}\n----------------".format(chunk,chunk_extra,extra,line,line_end,chunk_size,data))
                # check for end of message
                msg_end = chunk_extra.find(KDFSProtocol.END_MESSAGE)
                # if message end, then break
                if msg_end != -1:
                    break
            except Exception as e:
                KDFSProtocol.echo("raise an exception when receiving message",'protocol',e)
                # raise
                break

            # if counter > 30: break
        
        # KDFSProtocol.echo('data resv:{},is_file:{}'.format(data,is_file),'debug')
        # return empty, if data is empty
        if len(data) == 0:
            return None
        # if not file, then decode it
        if not is_file:
            message = json.loads(data.decode(KDFSProtocol.ENCODING))
            if type(message) is str:
                message = json.loads(message)
        else:
            try:
                message = gzip.decompress(data)
            except:
                message = data
        

        return message
    # -------------------------------------------------
    @staticmethod
    def sendCommandFormatter(command : str,params:dict={},send_queen=False,send_file=False,max_send_packets=1,recv_file=False) -> str:
        message : dict = {
            'command'   : command,
            'params'    : params,
            'send_by'   : 'queen' if send_queen else 'client',
            'send_file' : send_file,
            'receive_file': recv_file,
            'max_packets' : max_send_packets
        }

        return json.dumps(message)
    # -------------------------------------------------
    @staticmethod
    def sendResponseFormatter(response,errors:list=[],meta:dict={}) -> str:
        # trim errors
        tmp_errors = []
        for error in errors:
            if len(error) != 0:
                tmp_errors.append(error)
        errors = tmp_errors

        message : dict = {
            'data'   : response,
            'errors' : errors,
            'meta'   : meta
        }

        return json.dumps(message)
    # -------------------------------------------------
    @staticmethod
    def sendMessage(socketi : socket.socket,chunk_size : int,data,send_file=False):
        # check for socket not valid
        if socketi == None: return
        # decode data by encoding, if not file!
        if not send_file or type(data) is str:
            data = data.encode(KDFSProtocol.ENCODING)
        else:
            #=> compress content by gzip
            data = gzip.compress(data,KDFSProtocol.COMPRESS_LEVEL)
        # check for chunk size
        chunk_size = KDFSProtocol.checkChunkSize(chunk_size)
        #=>calc data chunks count
        dataLen = len(data)
        dataChunks = math.ceil(dataLen / chunk_size)
        # KDFSProtocol.echo("Send Data chunks:{} ({} bytes)".format(dataChunks,dataLen),'protocol')
        #=>send data chunks
        for i in range(0,dataChunks,1):
            try:
                chunk = data[i*chunk_size:i*chunk_size+chunk_size]
                # append end chunk
                chunk += KDFSProtocol.END_CHUNK
                # if last chunk, then append end message
                if i+1 == dataChunks:
                    chunk += KDFSProtocol.END_MESSAGE
                # KDFSProtocol.echo('(debug) send chunk:',chunk)
                socketi.send(chunk)
            except (Exception,KeyboardInterrupt) as e:
                KDFSProtocol.echo('Raise an exception on sending chunks','protocol',e,is_err=True)
                return
    # -------------------------------------------------
    @staticmethod
    def echo(msg:str,frm:str='KDFS',err='',end='\n',is_err=False):
        currentDatetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if type(frm) is str: frm = frm.upper()
        else: frm = str(frm)
        log = ''
        log_mode = 'INFO'
        log_msg = msg

        if type(err) is not str: err = str(err)

        if err == '' and not is_err:
            print("{} [{}]\t{}".format(
                colored(f"(INFO:{frm[0:7]: ^7})",'blue',attrs=['bold']),
                currentDatetime,
                msg
                ),end=end,file=sys.stdout)
        else:
            # append error message to msg, if exist
            logo_mode = 'ERROR'
            if err != '' and err != None:
                msg = "{} ({})".format(msg,colored(err,'red'))
                log_msg = "{} ({})".format(msg,err)

            print("{} [{}]\t{}".format(
                colored(f"(ERR :{frm[0:7]: ^7})",'red',attrs=['bold']),
                currentDatetime,
                msg
            ),file=sys.stderr)
        # log system
        from server.ServerUtils import ServerUtils as utils
        # append new log to logs file
        with open(utils.LOGS_PATH,'a') as f:
            f.write("{} {} [{}] {}\n".format(currentDatetime,log_mode,f"{frm[0:10]: ^10}",msg))