#!/bin/bash
#sudo node /home/nokia/OLSM/Agv/server.js > /dev/null 2>&1 &
node /home/nokia/OLSM/Agv/server.js > /dev/null &
python3 /home/nokia/OLSM/Agv/agv.py  > /dev/null &
