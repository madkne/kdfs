#! /bin/bash
# pgrep "python3 server.py start" | xargs kill -9
killall -9 python3
clear
rm nohup.out
nohup python3 server.py start > nohup.out & 
# python3 server.py start