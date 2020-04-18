
import socket

class KDFSQueen:
    GLOBAL_PORT = 4040

    def __init__(self,port,start_ip:str,end_ip:str):
        self.GLOBAL_PORT = port
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
                print("(queen) check for 192.168.{}.{} : ".format(i,j),end=' ')
                socket = self.socketConnect(f"192.168.{i}.{j}",self.GLOBAL_PORT)
                try:
                    # send identify command
                    socket.send("identify".encode('utf-8'))
                    # get response of command, if exist!
                    response = socket.recv(1024)
                    print("\t***ACCEPT***")
                    print ('Received', repr(response))
                except Exception:
                    print("\tREJECT")
                finally:
                    # close socket 
                    socket.close()
                

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