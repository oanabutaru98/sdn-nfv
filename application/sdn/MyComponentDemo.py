from pox.core import core
from pox.lib.util import dpid_to_str
import pox.openflow.libopenflow_01 as of
from l2_learning import LearningSwitch
from BaseFirewall import BaseFirewall
from Firewall1 import Firewall1
from Firewall2 import Firewall2
import traceback
import sys
import subprocess

log = core.getLogger()

class MyComponent (object):
	
	def __init__ (self):
		core.openflow.addListeners(self)

	def launch_click(self, dpid, configuration, name):

		cmd = "sudo click " + configuration + " > ../nfv/" + configuration + ".out 2>&1 &"
		log.info("Launching click for " + name + " with command " + cmd)
		p = subprocess.Popen(cmd, shell = True)
		log.info("Click launched for " + name + " with PID " + str(p.pid))
				

	def _handle_ConnectionUp (self, event):
		minRegularSwitchDpid = 1
		maxRegularSwitchDpid = 4
		
		if(event.dpid == 7):
			log.info("Starting a Click process for %d" % event.dpid)
			self.launch_click(event.dpid, "../nfv/ids.click", "IDS")


		if(event.dpid == 8):
                        log.info("Starting a Click process for %d" % event.dpid)
                        self.launch_click(event.dpid, "../nfv/lb1.click", "LB1")

		if(event.dpid == 9):
                        log.info("Starting a Click process for %d" % event.dpid)
                        self.launch_click(event.dpid, "../nfv/napt.click", "NAPT")
	
		if (event.dpid >= minRegularSwitchDpid and event.dpid <= maxRegularSwitchDpid):
			try:
				log.info("Treating %s as l2_learning switch", event.connection)
				regularSwitch = LearningSwitch(event.connection, False)
				log.info("Switch %s has come up!!",dpid_to_str(event.dpid))
				#regularSwitch._handle_PacketIn(event.parsed)
				#regularSwitch._handle_PacketIn(event)
			except Exception as e:
				log.info("Error creating learning switch")
				tb = traceback.format_exc()
				print tb
		if (event.dpid == 5):
			try:
				log.info("Treating %s as firewall 1", event.connection)
				firewall = Firewall1(event.connection, False)
				log.info("Switch %s has come up!!", dpid_to_str(event.dpid))
			except Exception as e:
				log.info("Error creating firewall 1")
				tb = traceback.format_exc()
				print tb

		if (event.dpid == 6):
                        try:
                                log.info("Treating %s as firewall 2", event.connection)
                                firewall = Firewall2(event.connection, False)
                                log.info("Switch %s has come up!!", dpid_to_str(event.dpid))
                        except Exception as e:
                                log.info("Error creating firewall 2")
                                tb = traceback.format_exc()
                                print tb

def launch ():
	core.registerNew(MyComponent)
