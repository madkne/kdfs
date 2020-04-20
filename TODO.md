

# TODO
## start from 2020.4.16

- [x] open and read config file
- [x] open sample socket server
- [x] try to connect to another soket in another system
- [x] start queen server as service
- [x] scan all up hosts in local network by queen server
- [x] create identify command
- [x] send command by chunks
- [x] get command by chunks
- [x] get command and mapped in commands
- [x] send identify response to queen
- [x] verify nodes of kdfs
- [x] update nodes
- [x] create kdfs client
- [x] check for listenning kdfs server on client
- [x] update state of nodes (on/off)
- [x] return list of all nodes if path is empty for list command
- [x] formatting table mode response in client
- [x] complete 'list' command for clients
- [ ] check permissions of clients
- [x] compress files for sending and decompress for retrieving
- [x] start 'upgrade' command for servers
- [x] create upgrader bash script
- [x] complete 'upgrade' command for servers
- [ ] complete 'notify' command for clients
- [ ] complete 'info' command for clients
- [ ] add logs system to servers


## Bugs

- [ ] check client servers if queen_port is blocked by firewall
- [ ] check for unique queen on kdfs system
- [x] check for ports not already used
- [x] validate old ip addresses of nodes by queen
- [x] save and restore queen_ip in config