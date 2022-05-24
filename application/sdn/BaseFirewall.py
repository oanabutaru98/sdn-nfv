from pox.core import core
from pox.lib.util import dpid_to_str
import pox.openflow.libopenflow_01 as of
from pox.forwarding.l2_learning import LearningSwitch
import traceback
import sys

log = core.getLogger()


class BaseFirewall(LearningSwitch):

	def __init__(self,connection,transparent):
		super(BaseFirewall, self).__init__(connection, transparent)
 	
	def _handle_PacketIn (self,event):

		packet = event.parsed
        	
		def drop (duration = None):
      			if duration is not None:
        			if not isinstance(duration, tuple):
          				duration = (duration,duration)
        			msg = of.ofp_flow_mod()
        			msg.match = of.ofp_match.from_packet(packet)
        			msg.idle_timeout = 5    # duration[0]
        			msg.hard_timeout = 5          # duration[1]
        			msg.buffer_id = event.ofp.buffer_id
        			self.connection.send(msg)
      			elif event.ofp.buffer_id != -1:
        			msg = of.ofp_packet_out()
        			msg.buffer_id = event.ofp.buffer_id
        			msg.in_port = event.port
        			self.connection.send(msg)

		switch_port= event.port
		parsed = packet.parsed
		if not parsed:
			log.info("ignoring incomplete packet")
			return

		if not self.checkForFirewallRules(event, switch_port):
			log.info("Package dropped")
			drop(10)
		else: 
			super(BaseFirewall, self)._handle_PacketIn(event, True)

	def checkForFirewallRules (self, event, switch_port):
		if not self.checkSpecificFirewallRules(event, switch_port):
			log.info("check for firewall rules not passed")
			return False 

		else: 
			log.info("check for firewall rules passed")
			return True

	def checkSpecificFirewallRules (self, event, switch_port):
		log.info("choosing specific firewall")

def launch ():
	core.registerNew(BaseFirewall)
