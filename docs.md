
# KDFS : Kimia Distributed File System



## permissions

- basic (b)
- system (s)
- read (r)
- extra read (r+)
- content (c)
- write (w)
- extra write (w+)

## commands

### server-server

- identify : return mac address,version,os info
- upgrade : get version number of nodes and send source of queen server and client to them nodes and all nodes will restarted

### client-server(queen)

- nodes : return up nodes of kdfs list (perm:s)
- list [path] : return list of directories and files in [path] (perm:r)
- exist [path] : return boolean for check exist path (perm:r)
- info [mode=file] [path] : return info of file in path (perm:r+)
- move [mode=file|dir] [src_path] [dest_path] : move a file or directory from a source path to a dest path (perm:w+)
- delete [mode=file|dir] [path] : delete a file or directory by path (perm:w+)
- copy [mode=file|dir] [src_path] [dest_path] : copy a file or directory from a source path to a dest path (perm:w)
- create [mode=file|dir] [path] : create a file or directory in a path (perm:w)
- pwd : display current path and node name (perm:b)
- info [mode=storage] : display current nodestorage info (perm:b)
- download [kdfs_path] [local_path] : download file from kdfs to local filesystem (perm:c)
- upload [local_path] [kdfs_path] : upload file from local to kdfs (perm:w)