SHELL := /bin/bash
current_dir:=$(shell pwd)

prepare_pox:
	sudo ./setup_pox.sh
app: prepare_pox
	@cd application/sdn/ && sudo make start

app_background: prepare_pox
	@cd application/sdn/ && sudo make start_background
topo:
	@cd topology/ && sudo make topo

test_var:
	@echo ${current_dir}
	@cd ${current_dir}/topology; pwd

test: prepare_pox
	sudo ./build.sh	

clean_essential:
	@echo -n "Cleaning Mininet...    "
	@cd topology/ && sudo make clean
	@echo -n "Cleaning POX...      " 
	@(cd application/sdn/ && sudo make clean) || true
	@echo -n "System cleanup completed !	\n"
clean_report:
	@echo -n "Remove all test file results! \n"	

clean: clean_report clean_essential
