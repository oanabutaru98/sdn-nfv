POX_PATH:=$(echo pwd)
PORT_NUM:=6633
#POX_APP:=$(echo pwd)./pox.py openflow.of_01 --port=${PORT_NUM} log.level --DEBUG log --file=./myLog.log 
POX_APP:=$(echo pwd)./pox.py 
# POX_APP:=$(echo pwd)./pox.py log.level --DEBUG log --file=./myLog.log 

MODULE:=MyComponentDemo

start:
	@sudo python $(POX_APP) $(MODULE)

start_background:
	@sudo python $(POX_APP) $(MODULE) &
clean:
	@sudo rm -rf *.pyc
	@sudo rm -rf pox
	@sudo rm pox.py
	@sudo fuser -k ${PORT_NUM}/tcp
