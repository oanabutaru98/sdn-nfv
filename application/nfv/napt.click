define($PORT1 sw9-eth1, $PORT2 sw9-eth2)

define($PbAddr 100.0.0.1, $PrAddr 10.0.0.1)

eth1_in, eth2_in, eth1_out, eth2_out :: AverageCounter

eth1_in_total, eth1_out_total, eth2_in_total, eth2_out_total :: Counter

tcp_arp_req_in, tcp_arp_res_in, tcp_arp_req_out, tcp_arp_res_out :: Counter

tcp_discard_in_1, tcp_discard_in_2:: Counter
tcp_discard_out_1, tcp_discard_out_2:: Counter

icmp_in_1, icmp_in_2, icmp_out_1, icmp_out_2:: Counter

service_in, service_out :: Counter

// From where to pick packets
fd1::FromDevice($PORT1, SNIFFER false, METHOD LINUX, PROMISC true)
fd2::FromDevice($PORT2, SNIFFER false, METHOD LINUX, PROMISC true)

// Where to send packets
td1:: Queue -> eth1_out_total -> eth1_out -> ToDevice($PORT1, METHOD LINUX)
td2:: Queue -> eth2_out_total -> eth2_out -> ToDevice($PORT2, METHOD LINUX)

tcp_classifier_in, tcp_classifier_out :: Classifier(12/0806 20/0001, // ARP Request
			   			  12/0806 20/0002, // ARP Reply
			   			  12/0800,         // IP
			   			  -)

ip_classifier_in, ip_classifier_out :: IPClassifier(tcp,
			    				icmp type 0,
							icmp type 8,
							-)

//IPRewriter(pattern A1 P1 A2 P2 O OR)
// A1 - new source address
// P1 - new source port
// A2 - new destination address
// P2 - new destination port
// O - output port number
// OR - used for written reply packets

ip_rewriter :: IPRewriter(pattern $PbAddr 50001-55000 - - 0 1)
icmp_rewriter :: ICMPPingRewriter(pattern $PbAddr 50001-55000 - - 0 1)

arp_resp_out :: ARPResponder($PbAddr $PORT2)
arp_resp_in :: ARPResponder($PrAddr $PORT1);
arp_quer_out :: ARPQuerier($PbAddr, $PORT2);
arp_quer_in :: ARPQuerier($PrAddr, $PORT1);

// incoming traffic
fd1 -> eth1_in_total -> eth1_in -> tcp_classifier_in
tcp_classifier_in[0] -> Print("incoming arp req") -> tcp_arp_req_in -> arp_resp_out[0] -> td1
tcp_classifier_in[1] -> Print("incoming arp repl") -> tcp_arp_res_in -> [1]arp_quer_out
tcp_classifier_in[2] -> Print("incoming ip packet") -> Strip(14) -> CheckIPHeader -> ip_classifier_in
tcp_classifier_in[3] -> tcp_discard_in_1 -> Print("incoming something else, discard") -> Discard

ip_classifier_in[0] -> service_in -> Print("incoming tcp packet") -> ip_rewriter[1] -> [0]arp_quer_in -> td2
ip_classifier_in[1] -> icmp_in_1 -> Print("incoming icmp type 0") -> icmp_rewriter[1] -> [0]arp_quer_in -> td2
ip_classifier_in[2] -> icmp_in_2 -> Print("incoming icmp type 8") -> ICMPPingResponder -> [0]arp_quer_out -> td1
ip_classifier_in[3] -> tcp_discard_in_2 -> Print("incoming something else in ip, discard") -> Discard

// outgoing traffic
fd2 -> eth2_in_total -> eth2_in -> tcp_classifier_out
tcp_classifier_out[0] -> Print("outgoing arp req") -> tcp_arp_req_out -> arp_resp_in[0] -> td2
tcp_classifier_out[1] -> Print("outgoing arp repl") -> tcp_arp_res_out -> [1]arp_quer_in
tcp_classifier_out[2] -> Print("outgoing ip packet") -> Strip(14) -> CheckIPHeader -> ip_classifier_out
tcp_classifier_out[3] -> tcp_discard_out_1 -> Print("outgoing something else, discard", -1) -> Discard

ip_classifier_out[0] -> service_out -> Print("outgoing tcp packet") -> ip_rewriter[0] -> [0]arp_quer_out -> td1
ip_classifier_out[1] -> icmp_out_1 -> Print("outgoing icmp type 0") -> Discard
ip_classifier_out[2] -> icmp_out_2 -> Print("outgoing icmp type 8") -> icmp_rewriter[0] -> [0]arp_quer_out -> td1
ip_classifier_out[3] -> tcp_discard_out_2 -> Print("outgoing something else ip, discard") -> Discard

DriverManager(wait, print > ../../results/napt.report "
                =============== NAPT Report =================
                Input Packet rate (pps) : $(add $(eth1_in.rate) $(eth2_in.rate)),
                Output Packet rate (pps) : $(add $(eth1_out.rate) $(eth2_out.rate)),
                
                Total # of input packets : $(add $(eth1_in_total.count) $(eth2_in_total.count)),
                Total # of output packets : $(add $(eth1_out_total.count) $(eth2_out_total.count)),
                
                Total # of ARP requests : $(add $(tcp_arp_req_in.count) $(tcp_arp_req_out.count)),
               	Total # of ARP response : $(add $(tcp_arp_res_in.count) $(tcp_arp_res_out.count)),
                
                Total # of service packets : $(add $(service_in.count) $(service_out.count)),
                Total # of ICMP packets : $(add $(icmp_in_1.count) $(icmp_in_2.count) $(icmp_out_1.count) $(icmp_out_2.count)),
                Total # of dropped packets : $(add $(tcp_discard_in_1.count) $(tcp_discard_in_2.count) $(tcp_discard_out_1.count) $(tcp_discard_out_2.count)),
                ==============================================",
		stop);


