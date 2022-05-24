#!/bin/bash

sudo cp -r ../../pox/pox ./application/sdn
sudo cp ../../pox/pox.py ./application/sdn
cd application/sdn/pox/forwarding
sudo rm l2_learning.py
cd ../../../..
sudo cp ./application/sdn/l2_learning.py ./application/sdn/pox/forwarding
