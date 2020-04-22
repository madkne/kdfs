
# KDFS : Kimia Distributed File System

KDFS is a distributed file system containse multiple nodes and a node can be a laptop, old computer and all devices can run a python web server and connect to local network!

## let's Start!

> every node in KDFS includes a server (for listenning commands from queen) and a client (for type commands and send it to queen)

1. KDFS works in local network and in startup defined a Queen node (for managing all nodes) and then run kdfs server on every system on local network.
2. then kdfs queen server scan all local network (by IP range) and find up nodes.
3. then by 'add' command you can add all scaned nodes.

## permissions for every node

> every node can have many permissions for executing commands by client and their defined in queen node database

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
  - upgrade.sh

## commands

### server-server

- identify : return mac address,version,os info
- upgrade [version] : get version number of nodes and send source of queen server and client to them nodes and all nodes will restarted

### client-server(queen)
  
- [x] list [path?] : return list of directories and files in [path] and if not have any path return list of nodes diretories (like drives) (perm:r)
  
        > list *://home/
        > list
        > list pc1://

- [x] notify [text] : send and show a notify text to all nodes of kdfs (perm:s)

- [x] stat [path] : return info of file or directory in path (perm:r+)

- [x] exist [path] : return boolean for check exist path (perm:r)

- [ ] find [mode=name|content] [type=rec|file] [path] [regex] : find by text (include simple regular expression) in filenames, direnames and contents and return list of find paths (perm:c,r)

#### Reqgular Expression Rules:

* %  : bl% finds bl, black, blue, and blob (zero,one,or many chars)
* _  : h_t finds hot, hat, and hit (just one char)
* \#  : 2#5 finds 205, 215, 225, 235, 245, 255, 265, 275, 285, and 295 (just one number(0-9))
* samples : 'a__%','%a','a%o'
  
        > find name file "*://" "sam%-###.txt"
        > find content all "pc1://home/" "%hello world!%"
        > find name dir "*://" ".%"



- [ ] move [mode=file|dir] [src_path] [dest_path] : move a file or directory from a source path to a dest path (perm:w+)
  
- [ ] delete [mode=file|dir] [path] : delete a file or directory by path (perm:w+)
  
- [ ] copy [mode=file|dir] [src_path] [dest_path] : copy a file or directory from a source path to a(all) dest path (perm:w)

        > copy file pc1://home/sam.txt pc2://home/sam2.txt
        > copy file pc1://sam.txt *://home

- [ ] create [mode=file|dir] [path] : create a file or directory in a(all) path and if parent not exist create them! (perm:w)

        > create file *://home/sam.txt
        > create dir pc1://home
  
<!-- - pwd : display current path and node name (perm:b) -->
  
- [ ] info [mode=storage] : display current nodestorage info (perm:b)
  
- [ ] download [kdfs_path] [local_path] : download file from kdfs to local filesystem (perm:c)
  
- [ ] upload [local_path] [kdfs_path] : upload file from local to kdfs (perm:w)

- [ ] add : scan all undefined nodes on local network and user can select one (perm:s)

- [ ] config [mode=set|get] [key] [value?] [nodename] : get or set kdfs config for a node (perm:s)

        > config set queen_port 2000 pc1
        > config get storage pc2

- [ ] nodes : return up nodes of kdfs list (perm:s)
