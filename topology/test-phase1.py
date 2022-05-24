from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Switch
from mininet.cli import CLI
from mininet.node import RemoteController
from mininet.node import OVSSwitch
import random
import time

global score
score = 0

class MyTopo( Topo ):

        def __init__( self ):

                Topo.__init__( self )

                # Add hosts
                h1 = self.addHost( 'h1', ip = '100.0.0.10/24' )
                h2 = self.addHost( 'h2', ip = '100.0.0.11/24' )
                h3 = self.addHost( 'h3', ip = '100.0.0.50/24')
                h4 = self.addHost( 'h4', ip = '100.0.0.51/24')

                # Add switches
                sw1 = self.addSwitch('sw1')
                sw2 = self.addSwitch('sw2')
                sw3 = self.addSwitch('sw3')
                sw4 = self.addSwitch('sw4')

                # Add firewalls
                fw1 = self.addSwitch('sw5')
                fw2 = self.addSwitch('sw6')

                # Add web servers
                ws1 = self.addHost('h5',ip='100.0.0.40/24')
 		ws2 = self.addHost('h6',ip='100.0.0.41/24')
                ws3 = self.addHost('h7',ip='100.0.0.42/24')

                # Add links
                self.addLink(h1, sw1)
                self.addLink(sw1, h2)
                self.addLink(sw1, fw1)
                self.addLink(fw1, sw2)
                self.addLink(sw2, sw4)
                self.addLink(sw4, ws1)
                self.addLink(sw4, ws2)
                self.addLink(sw4, ws3)
                self.addLink(sw2, fw2)
                self.addLink(fw2, sw3)
                self.addLink(sw3, h3)
                self.addLink(sw3, h4)

def setupTests(net):
	global host1 
	host1 = net.get('h1')
	global host2 
	host2 = net.get('h2')
	global host3 
	host3= net.get('h3')
	global host4
	host4 = net.get('h4')
	global host5
	host5 = net.get('h5')
	global host6
	host6 = net.get('h6')
	global host7
	host7 = net.get('h7') 

	global switch1
	switch1 = net.get('sw1')
	global switch2
	switch2 = net.get('sw2')
	global switch3
	switch3 = net.get('sw3')
	global switch4
	switch4 = net.get('sw4')
	global firewall1
	firewall1 = net.get('sw5')
	global firewall2
	firewall2 = net.get('sw6')

def startWebServers(net):
	print "Starting web servers..."
	for ws in [host5, host6, host7]:
		#web_server = net.get(ws)
		ws.cmd('python3 -m http.server 80 &')
		#print ("started " + ws)i
		time.sleep(3)
	print "Started web servers successfully"

def startTest1(net):
	global score	
	print "===== TEST 1 ====="
	res = net.pingAll(1)
	if int(res) == 52:
		print "100% success rate"
		print "PASSED"
		score += 1	
	else:
		print "FAILED"

def startTest2(net):
	global score
	print "====== TEST 2 ====="
	print "HTTP Access from PbZ to DmZ to port 80"
	pbz = ['h1', 'h2']
	dmz = ['100.0.0.40', '100.0.0.41', '100.0.0.42']
	prz = ['h3', 'h4']
	passed = True
	for host in pbz:
		host = net.get(host)
		for ws in dmz:
			#time.sleep(2)
			res = host.cmd('curl --ipv4 --connect-timeout 3 {}:80 -I'.format(ws))
			print "**"	
			print str(res)
			if "200 OK" in str(res):
				print "PASSED"
			else:
				passed = False
				print("Failed host " + str(host) + " curl ws " + str(ws))
				return
	
	if passed:
		score += 1

def startTest3(net):
	global score
        print "====== TEST 3 ====="
        print "HTTP Access from PrZ to DmZ to port 80"
        pbz = ['h1', 'h2']
        dmz = ['100.0.0.40', '100.0.0.41', '100.0.0.42']
        prz = ['h3', 'h4']
        passed = True
        for host in prz:
		host = net.get(host)
                for ws in dmz:
			#ws = net.get(ws)
                        res = host.cmd('curl -I --ipv4 --connect-timeout 2 {}:80'.format(ws))
                        print str(res)
                        if "200 OK" in str(res):
                                print("PASSED host " + str(host) + " curl ws " + str(ws))
                        else:
                                passed = False
                                print("Failed host " + str(host) + " curl ws " + str(ws))

        if passed:
                score += 1

def startTest4(net):
	global score
        print "====== TEST 4 ====="
        print "HTTP Access from PbZ to DmZ to a random port"
        pbz = ['h1', 'h2']
        dmz = ['100.0.0.40', '100.0.0.41', '100.0.0.42']
        prz = ['h3', 'h4']
	random_ports = []
	for i in range(0, 2):
		port = random.randint(1, 10000)
		random_ports.append(port)

        passed = True
        for host in pbz:
		host = net.get(host)
                for ws in dmz:
			#ws = net.get(ws)
			for port in random_ports:
                        	res = host.cmd('curl -I --ipv4 --connect-timeout 2 {}:{}'.format(ws, port))
                        	print str(res)
                        	if not "200 OK" in str(res):
                                	print "PASSED"
                        	else:
                                	passed = False
                                	print("Failed host " + str(host) + " curl ws " + str(ws))

        if passed:
                score += 1

def startTest5(net):
	global score
        print "====== TEST 5 ====="
        print "HTTP Access from PrZ to DmZ to a random port"
        pbz = ['h1', 'h2']
        dmz =  ['100.0.0.40', '100.0.0.41', '100.0.0.42']
        prz = ['h3', 'h4']
        passed = True
	random_ports = []
        
	for i in range(0, 2):
                port = random.randint(1, 10000)
                random_ports.append(port)

        for host in prz:
		host = net.get(host)
                for ws in dmz:
			#ws = net.get(ws)
			for port in random_ports:                        
				res = host.cmd('curl -I --ipv4 --connect-timeout 2 {}:{}'.format(ws, port))
                        	print str(res)
                        	if not "200 OK" in str(res):
                                	print "PASSED"
                        	else:
                                	passed = False
                                	print("Failed host " + str(host) + " curl ws " + str(ws))

        if passed:
                score += 1

def startTest6(net):
	global score
	print "====== TEST 6 ====="
	print "PING CURL PING from h3 to h7"
	host3 = net.get('h3')
	host7 = net.get('h7')
	res = net.ping([host3, host7], 2)
	print res
	if res == 0:
		print "FAILED"
		return
	else:
		res = host3.cmd('curl -I --ipv4 --connect-timeout 2 {}:80'.format('100.0.0.42'))
		print str(res)
		if not "200 OK" in str(res):
			print "FAILED"
			return
		else:
			res = net.ping([host3, host7], 2)
			if res == 0:
				print "FAILED"
			else:
				print "PASSED"
				score += 1
	

def startTest7(net):
	global score
	host3= net.get('h3')
	host1= net.get('h1')
	host1.cmd('python3 -m http.server 80 &')
	time.sleep(3)
        print "====== TEST 7 ====="
        print "CURL PING CURL from h3 to h1"
        res = host3.cmd('curl -I --ipv4 --connect-timeout 2 {}:80'.format('100.0.0.10'))
        print str(res)
        if not "200 OK" in str(res):
                print "FAILED"
                return
        else:
                res = host3.cmd('ping 100.0.0.10 -c1')
                if not "0% packet loss" in str(res):
                        print "FAILED"
                        return
                else:
                        res = host3.cmd('curl -I --ipv4 --connect-timeout 2 {}:80'.format('100.0.0.10'))
                        if not "200 OK" in str(res):
                                print "FAILED"
                        else:
                                print "PASSED"
                                score += 1

def startTests(net):
	startTest1(net)
	startTest2(net)
	startTest3(net)
	startTest4(net)
	startTest5(net)
	startTest6(net)
	startTest7(net)

def printTestScore():
	print "================="
	print "FINAL SCORE: " + str(score) + "/7"


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
		h.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
		h.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")
        
	for h in net.switches:
                h.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
                h.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
                h.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")
	
	net.start()

        #CLI( net )
	
	setupTests(net)	

	startWebServers(net)
	
	startTests(net)

	printTestScore()	
	

