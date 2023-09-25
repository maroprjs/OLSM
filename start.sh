#!/bin/bash
#sudo node /home/nokia/OLSM/Agv/server.js > /dev/null 2>&1 &
sleep 5
node /home/nokia/OLSM/Agv/server.js > /dev/null &
sleep 10
#python3 /home/nokia/OLSM/Agv/agv.py  > /dev/null &
python3 /home/nokia/OLSM/Agv/agv_smallSetup.py  > /dev/null &
