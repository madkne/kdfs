
# KDFS : Kimia Distributed File System



## permissions

- basic (b)
- system (s)
- read (r)
- extra read (r+)
- content (c)
- write (w)
- extra write (w+)

## required files and directories

- for queen server:
  - commands/
  - libs/
  - server/
  - database/
  - kdfs.conf
  - kdfs.py
  - server.py
- for other nodes servers:
  - commands/minimal.py
  - libs/
  - server/ - (KDFSQueen.py)
  - kdfs.conf
  - kdfs.py
  - server.py

## commands

### server-server

- identify : return mac address,version,os info
- upgrade : get version number of nodes and send source of queen server and client to them nodes and all nodes will restarted

### client-server(queen)

- nodes : return up nodes of kdfs list (perm:s)
  
- list [path?] : return list of directories and files in [path] and if not have any path return list of nodes diretories (like drives) (perm:r)
  
        > list *://home/
        > list
        > list pc1://

- exist [path] : return boolean for check exist path (perm:r)

- info [mode=file] [path] : return info of file in path (perm:r+)

- move [mode=file|dir] [src_path] [dest_path] : move a file or directory from a source path to a dest path (perm:w+)
  
- delete [mode=file|dir] [path] : delete a file or directory by path (perm:w+)
  
- copy [mode=file|dir] [src_path] [dest_path] : copy a file or directory from a source path to a(all) dest path (perm:w)

        > copy file pc1://home/sam.txt pc2://home/sam2.txt
        > copy file pc1://sam.txt *://home

- create [mode=file|dir] [path] : create a file or directory in a(all) path and if parent not exist create them! (perm:w)

        > create file *://home/sam.txt
        > create dir pc1://home
  
<!-- - pwd : display current path and node name (perm:b) -->
  
- info [mode=storage] : display current nodestorage info (perm:b)
  
- download [kdfs_path] [local_path] : download file from kdfs to local filesystem (perm:c)
  
- upload [local_path] [kdfs_path] : upload file from local to kdfs (perm:w)

- find [mode=name|content] [node=name|*] [text] : find by text in filenames, direnames and contents and return list of find paths (perm:c)
  
        > find name * sam
        > find content pc1 "hello world!"

- add : scan all undefined nodes on local network and user can select one (perm:s)

