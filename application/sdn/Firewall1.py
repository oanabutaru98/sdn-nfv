from pox.core import core
from pox.lib.util import dpid_to_str
import pox.openflow.libopenflow_01 as of
# from pox.forwarding.l2_learning import LearningSwitch
from BaseFirewall import BaseFirewall
import traceback
import sys
import pox.lib.packet as pkt

log = core.getLogger()

IP_TYPE = 2048;
TCP_PROTOCOL = 6;
ICMP_PROTOCOL = 1;
dmz_destinations = ['100.0.0.45']

class Firewall1(BaseFirewall):

	def __init__(self, connection, transparent):
		super(Firewall1, self).__init__(connection, transparent)

	def checkSpecificFirewallRules(self, event, switch_port):
		log.info("checking rules in firewall 1")
				
		packet = event.parsed
		if switch_port == 2:
			return self.checkIncoming(packet)		
		else: 
			return self.checkOutgoing(packet)
		
	def checkIncoming(self, packet):
		log.info("checking incoming traffic on firewall 1")
		return True	

	def checkOutgoing(self, packet):
		log.info("checking outgoing traffic on firewall 1")
		log.debug("packet TYPE : {0}".format(packet.type))
		match = of.ofp_match.from_packet(packet)
		if packet.type == IP_TYPE:
			ip_packet = packet.payload
			
			if packet.payload.protocol == ICMP_PROTOCOL and (packet.find("ipv4").payload.type == 0 or packet.find("ipv4").payload.type == 8):
				log.info("allowing icmp reply and requests from firewall 1")
				return True
			if ip_packet.protocol == TCP_PROTOCOL:
				destination = ip_packet.dstip
				log.info("TCP protocol destination: {0}".format(destination))
				if destination in dmz_destinations: 
					log.info("destination port : {0}".format(ip_packet.payload.dstport))
					if ip_packet.payload.dstport == 80:
						log.debug("it is toward dmz with port 80 allow")
						return True
				else:		 
					log.debug("toward a ip other than dmz, prob toward private zone allow")
					return True
				source = ip_packet.srcip
		elif match.dl_type == packet.ARP_TYPE:
			return True
		
		return False

def launch():
	core.registerNew(Firewall1)
