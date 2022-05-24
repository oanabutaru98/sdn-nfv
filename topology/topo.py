from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Switch
from mininet.cli import CLI
from mininet.node import RemoteController
from mininet.node import OVSSwitch

class MyTopo( Topo ):

	def __init__( self ):

		Topo.__init__( self )

		# Add hosts
		h1 = self.addHost( 'h1', ip = '100.0.0.10/24' )
		h2 = self.addHost( 'h2', ip = '100.0.0.11/24' )
		h3 = self.addHost( 'h3', ip = '10.0.0.50/24')
		h4 = self.addHost( 'h4', ip = '10.0.0.51/24')

		# Add switches
		sw1 = self.addSwitch('sw1')
		sw2 = self.addSwitch('sw2')
		sw3 = self.addSwitch('sw3')
		sw4 = self.addSwitch('sw4')
		
		# Add firewalls
		fw1 = self.addSwitch('sw5')
		fw2 = self.addSwitch('sw6')

		# Add click switches
		ids = self.addSwitch('sw7')
		lb1 = self.addSwitch('sw8')
		napt = self.addSwitch('sw9')

		# Add insp
		insp = self.addHost('h8',ip='100.0.0.30/24')

		# Add web servers
		ws1 = self.addHost('h5',ip='100.0.0.40/24')
		ws2 = self.addHost('h6',ip='100.0.0.41/24')
		ws3 = self.addHost('h7',ip='100.0.0.42/24')

		# Add links
		self.addLink(h1, sw1)
		self.addLink(sw1, h2)
		self.addLink(sw1, fw1)
		self.addLink(fw1, sw2)
		self.addLink(sw4, ws1)
		self.addLink(sw4, ws2)
		self.addLink(sw4, ws3)
		self.addLink(sw2, fw2)
		self.addLink(sw3, h3)
		self.addLink(sw3, h4)
		self.addLink(sw2, ids)
		self.addLink(ids, lb1)
		self.addLink(ids, insp)
		self.addLink(lb1, sw4)
		self.addLink(fw2, napt)
		self.addLink(napt, sw3)

def startWebServers(net):
	print("Starting web servers...")
	for ws in ['h5', 'h6', 'h7']:
		web_server = net.get(ws)
		# get the ip
		ip_addr = web_server.IP()
		# web_server.cmd('python3 -m http.server 80 &')
		web_server.cmd('python3 http_server_multithread.py {} 80 &'.format(str(ip_addr)))
		#print ("started " + ws)
	print("Started web servers successfully")

if __name__ == "__main__":

	topo = MyTopo()

	ctrl = RemoteController("c0", ip="127.0.0.1", port=6633) 

	net = Mininet(
			topo  = topo,
			switch = OVSSwitch,
			controller = ctrl,
			autoSetMacs = True,
			autoStaticArp = True,
			build = True,
			cleanup = True
		     )
	for h in net.hosts:
		h.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
	
	startWebServers(net)
	
	for PrZ_host in ["h3", "h4"]:
		h = net.get(PrZ_host)
		h.cmd("ip route add default via 10.0.0.1")
	
	net.get('h8').cmd("sudo tcpdump -i h8-eth0 -vvv tcp -w ../results/ids_capture.pcap &")
	net.start()

	CLI( net )
