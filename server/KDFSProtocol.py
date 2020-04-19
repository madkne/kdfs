
import socket
import json
import math

class KDFSProtocol:
    END_CHUNK = b'\r!\n'
    END_MESSAGE = b'\r!END!\r--\n'
    ENCODING = 'UTF-8'
    MESSAGE_TYPE = 'JSON'
    # -------------------------------------------------
    @staticmethod
    def checkChunkSize(chunk_size : int):
        if chunk_size < 2 + len(KDFSProtocol.END_CHUNK + KDFSProtocol.END_MESSAGE):
            return 2 + len(KDFSProtocol.END_CHUNK + KDFSProtocol.END_MESSAGE)
        return chunk_size
    # -------------------------------------------------
    @staticmethod
    def receiveMessage(socketi : socket.socket,chunk_size : int,is_file=False) -> dict:
        # check for socket not valid
        if socketi == None: return
        message : dict = {}
        data = b''
        line = b''
        extra = b''
        counter = 0
        # check for chunk size
        chunk_size = KDFSProtocol.checkChunkSize(chunk_size)
        # iterate on socket to get complete data
        while True:
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
            # print("(debug) chunk:{}\nchunk_extra:{} (extra:{})\nline:{} (line_end:{},chunk_size:{})\ndata:{}\n----------------".format(chunk,chunk_extra,extra,line,line_end,chunk_size,data))
            # check for end of message
            msg_end = chunk_extra.find(KDFSProtocol.END_MESSAGE)
            # if message end, then break
            if msg_end != -1:
                break

            # if counter > 30: break
        
        # print('(protocol) data resv:',data)
        # return empty, if data is empty
        if len(data) == 0:
            return ''
        # if not file, then decode it
        if not is_file:
            message = json.loads(data.decode(KDFSProtocol.ENCODING))
            if type(message) is str:
                message = json.loads(message)
        # else:
        #     message
        # TODO:
        

        return message
    # -------------------------------------------------
    @staticmethod
    def sendCommandFormatter(command : str,params:dict={},send_queen=False) -> str:
        message : dict = {
            'command'   : command,
            'params'    : params,
            'send_by'   : 'queen' if send_queen else 'client'
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
    def sendMessage(socketi : socket.socket,chunk_size : int,data : str,is_file=False):
        # check for socket not valid
        if socketi == None: return
        # decode data by encoding, if not file!
        if not is_file:
            data = data.encode(KDFSProtocol.ENCODING)
        # check for chunk size
        chunk_size = KDFSProtocol.checkChunkSize(chunk_size)
        #=>calc data chunks count
        dataLen = len(data)
        dataChunks = math.ceil(dataLen / chunk_size)
        # print("(protocol) Send Data chunks:{} ({} bytes)".format(dataChunks,dataLen))
        #=>send data chunks
        for i in range(0,dataChunks,1):
            chunk = data[i*chunk_size:i*chunk_size+chunk_size]
            # append end chunk
            chunk += KDFSProtocol.END_CHUNK
            # if last chunk, then append end message
            if i+1 == dataChunks:
                chunk += KDFSProtocol.END_MESSAGE
            # print('(debug) send chunk:',chunk)
            socketi.send(chunk)