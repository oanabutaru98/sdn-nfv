// PORT1 facing ids, PORT2  facing to the DMZ
define($PORT1 sw8-eth1, $PORT2 sw8-eth2)
define($to_ids_ip 100.0.0.45)
// the actual ip address of DMz servers
define($s1 100.0.0.40, $s2 100.0.0.41, $s3 100.0.0.42)
// allowed protocol && port number
define($proto tcp, $port 80)
// s :: EtherSwitch;

eth1_in, eth2_in, eth1_out, eth2_out:: AverageCounter
eth1_in_total, eth2_in_total, eth1_out_total, eth2_out_total:: Counter
discard_1, discard_2, discard_3, discard_4:: Counter
arp_req_in, arp_req_out, arp_res_in, arp_res_out :: Counter
service_1, service_2:: Counter
icmp_1, icmp_2, icmp_3:: Counter




// From where to pick packets
fd1::FromDevice($PORT1, SNIFFER false, METHOD LINUX, PROMISC true)
fd2::FromDevice($PORT2, SNIFFER false, METHOD LINUX, PROMISC true)

// // Where to send packets
// Where to send packets
td1::Queue -> eth1_out -> eth1_out_total -> ToDevice($PORT1, METHOD LINUX)
td2::Queue -> eth2_out -> eth2_out_total -> ToDevice($PORT2, METHOD LINUX)


// ARPR, ARR , IP Classifiers
fd1 -> eth1_in -> eth1_in_total -> fd1_classifier :: Classifier(12/0806 20/0001, 12/0806 20/0002, 12/0800, -);
fd2 -> eth2_in -> eth2_in_total -> fd2_classifier :: Classifier(12/0806 20/0001, 12/0806 20/0002, 12/0800, -);

arp_response_ext :: ARPResponder($to_ids_ip $PORT1);
arp_response_int :: ARPResponder($to_ids_ip $PORT2);
arp_querier_extif :: ARPQuerier($to_ids_ip, $PORT1);
arp_querier_intif :: ARPQuerier($to_ids_ip, $PORT2)

// respond to ARP queries  for the router external interface

fd1_classifier[0] -> Print("From External ARP_Req") -> arp_req_out -> arp_response_ext -> td1 ;
fd1_classifier[1] -> Print("From External ARP Response") -> arp_res_out -> [1]arp_querier_extif;

// respond to ARP queries for the router internal interface
fd2_classifier[0] -> Print("From Internal ARP_Req") -> arp_req_in -> arp_response_int -> td2 ;
fd2_classifier[1] -> Print("From Internal ARP Response") -> arp_res_in -> [1]arp_querier_intif;

// return to ext, and go through an arp queriere in case the Ethernet addr unknown
td1_arp :: CheckIPHeader -> [0]arp_querier_extif -> td1;
// return to int, and go through an arp queriere in case the Ethernet addr unknown
td2_arp :: CheckIPHeader -> [0]arp_querier_intif -> td2;

// Classifying IP traffic
fd1_classifier[2] -> Print("From External IP Packet") -> service_1 -> Strip(14) -> CheckIPHeader
	-> fd1_ipc :: IPClassifier(
	// ping from out to DMZ
		icmp && icmp type echo && dst $to_ids_ip,
	// ping from out to servers (not allowed)
		icmp && icmp type echo && (dst $s1 || dst $s2 || dst $s3),
	//  tcp traffic  from ext to lb
		dst $to_ids_ip && $proto port $port,
	// ping resp to rewrited ping
		proto icmp && icmp type echo-reply,
	// others
		-
	);

fd2_classifier[2] -> Print("From Internal IP Packet") -> service_2 -> Strip(14) -> CheckIPHeader
	-> fd2_ipc :: IPClassifier(
	// tcp from int to ext
		$proto,
	// pings req to rewrite
		icmp && icmp type echo && dst != $to_ids_ip,
	// ping from in to in
		icmp && icmp type echo && dst $to_ids_ip, 
	// others
		-
		);

// PING BACK
// send back pings reply from lb1 virtual IP to outside
fd1_ipc[0] -> Print("ICMP ECHO from ext -> dmz") -> ICMPPingResponder -> icmp_1 -> Print("Before to td1_arp get ip addres", 200) -> td1_arp ;

// send back pings error DMZ to outside
//host - unreachable
// ICMPError(SRC, TYPE [, CODE, keywords BADADDRS, MTU])  3 - unreachable  1 - host
fd1_ipc[1] -> Print("ICMP ECHO from ext -> in") -> ICMPError($to_ids_ip, 3, 1 ) -> icmp_2 -> Print("Before to td1_arp get ip addres", 200) -> td1_arp ; 


// port 0 to ids, port 1 to the DMZ
ping_rw :: ICMPPingRewriter(pattern $to_ids_ip 1025-65535 - - 0 1)

// rewrite ip to the inner server ip address (real ip)
ping_rw[1] -> td2_arp
// rewrite ip to the lb1 virtual ip address
ping_rw[0] -> td1_arp

//IPRewriter(pattern A1 P1 A2 P2 O OR)
// A1 - new source address
// P1 - new source port
// A2 - new destination address
// P2 - new destination port
// O - output port number
// OR - used for written reply packets

roundroubin :: RoundRobinIPMapper( $to_ids_ip - $s1 - 0 1,
						  $to_ids_ip - $s2 - 0 1,
						  $to_ids_ip - $s3 - 0 1
						)
rw :: IPRewriter(roundroubin);

// change the destination to the real server ip address and send to the server
rw[0] -> SetTCPChecksum -> td2_arp;
// change the destination to the lb virtual ip and send to the outside world
rw[1] -> SetTCPChecksum -> td1_arp;

// From EXTERNAL

// fd1_ipc[2] -> Print("IP from EXT to INT") -> [0]rw;
fd1_ipc[2] -> Print("IP from EXT to INT") -> rw;
// fd1_ipc[3] -> Print("ICMP from EXT to INT") -> [0]ping_rw;
fd1_ipc[3] -> Print("ICMP from EXT to INT") -> ping_rw;


// From INTERNAL

fd2_ipc[0] -> Print("IP from INT to EXT") -> rw;
fd2_ipc[1] -> Print("ICMP from INT to EXT") -> ping_rw;

// send back pings to inside from inside
fd2_ipc[2] -> Print("ICMP ECHO From INT -> INT") -> ICMPPingResponder -> icmp_3 -> Print("Before to td2_arp get ip addres", 200) -> td2_arp;

//Discard non-IP, non-ARP packets 
fd1_classifier[3] -> Print("Discarding non IP Packet") -> discard_1 -> Discard;
fd2_classifier[3] -> Print("Discarding non IP Packet") -> discard_2 -> Discard;

fd1_ipc[4] -> Print("Discarding unwanted IP Packet") -> discard_3 -> Discard;
fd2_ipc[3] -> Print("Discarding unwanted IP Packet") -> discard_4 -> Discard;


DriverManager(wait , print > ../../results/lb1.report "
	=================== LB  Report ===================
	Input Packet Rate (pps): $(add $(eth1_in.rate) $(eth2_in.rate))
	Output Packet Rate(pps): $(add $(eth1_out.rate) $(eth2_out.rate))
	Total # of ARP requests packets: $(add $(arp_req_in.count) $(arp_req_out.count))
	Total # of ARP responses packets: $(add $(arp_res_in.count) $(arp_res_out.count))
	Total # of service requests packets: $(add $(service_1.count) $(service_2.count))
	Total # of ICMP packets: $(add $(icmp_1.count) $(icmp_2.count) $(icmp_3.count))
	Total # of input packets: $(add $(eth1_in_total.count) $(eth2_in_total.count))
	Total # of output packets: $(add $(eth1_out_total.count) $(eth2_out_total.count))
	Total # of dropped packets: $(add $(discard_1.count) $(discard_2.count) $(discard_3.count) $(discard_4.count) )
	==================================================" , 
	stop);
