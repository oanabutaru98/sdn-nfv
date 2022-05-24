from pox.core import core
from pox.lib.util import dpid_to_str
import pox.openflow.libopenflow_01 as of
# from pox.forwarding.l2_learning import LearningSwitch
from BaseFirewall import BaseFirewall
import traceback
import sys

log = core.getLogger()
IP_TYPE = 2048;
ARP_TYPE = 2054;
IPV6_TYPE = 34525
dmz_destinations = ['100.0.0.40', '100.0.0.41', '100.0.0.42', '100.0.0.45']
pbz_destinations = ['100.0.0.10', '100.0.0.11']
# src_port = 0 
ICMP_PROTOCOL = 1
TCP_PROTOCOL = 6

class Flow():
	def __init__(self, packet):

		self.charString = ""
		if packet.type != IPV6_TYPE:
			if packet.type != ARP_TYPE:
				self.protocol = packet.payload.protocol
				self.packet = packet
				self.parse_packet()
			elif packet.type == ARP_TYPE:
				# simply allow the packet
				self.type = ARP_TYPE
				self.protocol = "ARP"
				self.packet = packet
				self.charString = "ARP_TYPE"
		else:
			self.type = IPV6_TYPE
			log.debug("IPV6 packet recevied, drop!")
	def parse_packet(self):
		if self.packet.type == IP_TYPE:
			self.type = IP_TYPE
			self.charString += "IP_TYPE "
			self.srcip = self.packet.payload.srcip
			self.dstip = self.packet.payload.dstip
			self.charString += "srcip:{0} dstip:{1}".format(self.srcip, self.dstip)
		if self.protocol == TCP_PROTOCOL:
			self.src_port = self.packet.payload.payload.srcport
			self.dst_port = self.packet.payload.payload.dstport
			self.charString += "\nTCP src_port:{0} dst_port:{1}".format(self.src_port, self.dst_port)
		elif self.protocol == ICMP_PROTOCOL:
			self.icmp_type = self.packet.find("ipv4").payload.type
			self.charString += "\nICMP type:{0}".format(self.icmp_type)
	def isReply(self, incomingPacket):
		if self.type != incomingPacket.type:
			return False
		# todo allow other packets other than ip
		if self.type == IP_TYPE:
			incomingPayload = incomingPacket.payload
			if self.protocol != incomingPayload.protocol:
				return False
			# check IP
			if self.type == IP_TYPE:
				if (self.srcip != incomingPayload.dstip) or (self.dstip != incomingPayload.srcip):
					return False
				if self.protocol == TCP_PROTOCOL:
					if (self.src_port != incomingPayload.payload.dstport) or (self.dst_port != incomingPayload.payload.srcport):
						return False
				elif self.protocol == ICMP_PROTOCOL:
					if incomingPacket.find("ipv4").payload.type != 0:
						return False
		elif self.type == ARP_TYPE:
			return True
		return True
	def briefInfo(self):
		"""
		brief info
		"""
		log.info("============flow brief============")
		log.info(self.charString)

	def __eq__(self, other):
		if isinstance(other, Flow):
			if self.type != other.type:
				return False
			if self.type == IP_TYPE:
				try:
					if (self.srcip != other.srcip) or (self.dstip != other.dstip):
						return False
				except Exception as e:
					log.info("Exception caught in comparison Flow: %s" %(e))
					return False
			if self.protocol == TCP_PROTOCOL:
				try:
					if (self.src_port != other.src_port) or (self.dst_port != other.dst_port):
						return False
				except Exception as e:
					log.info("Exception caught in comparison Flow: %s" %(e))
					return False
			elif self.protocol == ICMP_PROTOCOL:
				try:
					if self.icmp_type != other.icmp_type:
						return False
				except Exception as e:
					log.info("Exception caught in comparison Flow: %s" %(e))
					return False
		return True

	def __ne__(self, other):
		return not self.__eq__(other)
	
	def __hash__(self):
		return hash(tuple(self.charString))

class Firewall2(BaseFirewall):

	def __init__(self, connection,transparent):
		self.flowRegistry = set()
		super(Firewall2, self).__init__(connection, transparent)
	
	def checkSpecificFirewallRules(self, event, switch_port):
		log.info("checking rules in firewall 2")

		packet = event.parsed
		if switch_port == 1:
			return self.checkIncoming(packet)
		else:
			return self.checkOutgoing(packet)

	def checkIncoming(self, packet):
		log.info("checking incoming traffic on firewall 2")


		for flow in self.flowRegistry:
			if flow.isReply(packet):
				log.info("incoming packet is a reply from a previous outgoing")
				flow.briefInfo()
				return True
		return False


	def checkOutgoing(self, packet):
		log.info("checking outgoing traffic on firewall 2")
		newFlow = Flow(packet)
		allowed = False
		if packet.type == IP_TYPE:
			ip_packet = packet.payload
			log.debug("*****************************************")
			log.debug("ip packet dstip: {}".format(ip_packet.dstip))
			if (ip_packet.protocol == TCP_PROTOCOL and ip_packet.payload.dstport == 80 and ip_packet.dstip in dmz_destinations):
				log.debug("yessss tcp to dmz on port 80")
				src_port = ip_packet.payload.srcport
				log.debug("source port:{0}".format(src_port))
				allowed = True
			if ip_packet.protocol==ICMP_PROTOCOL:
				allowed = True
			if (not allowed) and (ip_packet.dstip in pbz_destinations):
				log.debug("yesssss whateva to pbz")
				if ip_packet.protocol == TCP_PROTOCOL:
					src_port = ip_packet.payload.srcport
					log.debug("source port:{0}".format(src_port))
				allowed = True
		elif packet.type == ARP_TYPE:
			allowed = True
		if allowed:
			log.debug("********************")
			log.debug("Flow registered at fw2: ")
			log.debug(newFlow.briefInfo())
			self.flowRegistry.add(newFlow)
		return allowed
	

def launch():
	core.registerNew(Firewall2)
