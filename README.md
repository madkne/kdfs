
# KDFS : Kimia Distributed File System

KDFS is a distributed file system containse multiple nodes and a node can be a laptop, old computer and all devices can run a python web server and connect to local network!

This project is taken from the Hadoop Idea. but it is very simple and very useful for connecting all systems of local network for cloud computing like searching in files,managing all local network systems from one system or more (with more commands)!
KDFS is a cross platform, but not tested in windows or macos!!!

## let's Start!

> every node in KDFS includes a server (for listenning commands from queen) and a client (for type commands and send it to queen)

1. KDFS works in local network and in startup defined a Queen node (for managing all nodes) and then run kdfs server on every system on local network.
2. then kdfs queen server scan all local network (by IP range) and find up nodes.
3. then by 'add' command you can add all scaned nodes.

## commands

### server-server

- [x] identify : return mac address,version,os info
- [x] upgrade [version] : get version number of nodes and send source of queen server and client to them nodes and all nodes will restarted

### client-server(queen)
  
- [x] list [path?] : return list of directories and files in [path] and if not have any path return list of nodes diretories (like drives) (perm:r)
  
        > list *://home/
        > list
        > list pc1://

- [x] notify [text] : send and show a notify text to all nodes of kdfs (perm:s)

- [x] stat [path] : return info of file or directory in path (perm:r+)

- [x] exist [path] : return boolean for check exist path (perm:r)

- [x] find [mode=name|content] [type=rec|file] [path] [regex] : find by text (include simple regular expression) in filenames, direnames and contents and return list of find paths (perm:c,r)

#### Reqgular Expression Rules:

- [x] %  : bl% finds bl, black, blue, and blob (zero,one,or many chars)
- [x] _  : h_t finds hot, hat, and hit (just one char)
- [x] \#  : 2#5 finds 205, 215, 225, 235, 245, 255, 265, 275, 285, and 295 (just one number(0-9))
* samples : 'a__%','%a','a%o'
  
        > find name file "*://" "sam%-###.txt"
        > find content all "pc1://home/" "hello world!"
        > find name dir "*://" ".%"

- [ ] nodes [mode=add|show|change] [name?] [ip?|property?] [value?] (perm:s)
  - [x] nodes add [name?] [ip?]: scan all undefined nodes on local network and user can select one to add in nodes database

        > nodes add
        > nodes add pc4 "192.168.1.6"
  - [ ] nodes show [name?]: return up nodes of kdfs list

        > nodes show
        > nodes show pc3
  - [ ] nodes change [name] [property] [value] : if node exist, then change and update its property by new value


- [ ] move [mode=file|dir] [src_path] [dest_path] : move a file or directory from a source path to a dest path (perm:w+)
  
- [ ] delete [mode=file|dir] [path] : delete a file or directory by path (perm:w+)
  
- [ ] copy [mode=file|dir] [src_path] [dest_path] : copy a file or directory from a source path to a(all) dest path (perm:w)

        > copy file pc1://home/sam.txt pc2://home/sam2.txt
        > copy file pc1://sam.txt *://home

- [ ] create [mode=file|dir] [path] : create a file or directory in a(all) path and if parent not exist create them! (perm:w)

        > create file *://home/sam.txt
        > create dir pc1://home
  
- [ ] info [mode=storage] : display current nodestorage info (perm:b)
  
- [ ] download [kdfs_path] [local_path] : download file from kdfs to local filesystem (perm:c)
  
- [ ] upload [local_path] [kdfs_path] : upload file from local to kdfs (perm:w)

- [ ] config [mode=set|get] [key] [value?] [nodename] : get or set kdfs config for a node (perm:s)

        > config set queen_port 2000 pc1
        > config get storage pc2

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

## development

you can add more commands to KDFS!
your command can contains two sides:

1. queen side : for sending broardcast command to all nodes and manage response of them
   1. you must create a `.py` file in `commands/` directory and its name must same as command name
   2. in this file you must create a class by this name : `[command_name]Command`
   3. init a contractor like the other commands
   4. create `response` method and the end of this method, you should call parent response method like : `return super().response(res,err)`
2. nodes side : for executing command on every nodes that sending by queen server
   1. you must create a method in `commands/minimal.py -> MinimalCommands` class like : `[command_name]Command(self,params:dict)` 
   2. the end of this method should return two values (response,error)
   3. finally you should increase version number of config file of queen node and run queen server to auto upgrading all nodes by it!
   
## report BUGS

The project is under development and may have many bugs.
You can help us to find the basic bugs of this system to expand this project! :))