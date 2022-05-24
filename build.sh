#!/bin/bash
currentDir=$(pwd)
PORT_NUM=6633

cd application/sdn/ && sudo make start_background
# POX_ID=$(sudo python ./pox.py openflow.of_01 --port=6655 log.level --DEBUG log --file=./myLog.log MyComponentDemo &)
# controller_pid=$(sudo make start &)
# POX_PID=

# echo "controller pid"
# echo ${POX_ID}
# echo ${controller_pid}

# make test
cd ${currentDir} && cd topology && sudo make test

echo "test performed successfully now kill the click controller"
echo "Waiting for 2 seconds..."
sleep 2
# sudo kill -2 `ps -ef | grep 'pox.p[y]' | awk '{print $2}'` || true
# sudo kill -2 ${POX_ID}
sudo pkill --signal SIGINT click
echo "now delete the controller entirely"
cd ${currentDir} && sudo make clean_essential



