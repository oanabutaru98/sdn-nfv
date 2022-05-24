define($PORT1 sw7-eth1, $PORT2 sw7-eth2, $PORT3 sw7-eth3)
define($INJ1 143/636174202f6574632f706173737764,
      $INJ2 143/636174202f7661722f6c6f672f,
       $INJ3 142/494E53455254,
       $INJ4 142/555044415445,
       $INJ5 142/44454C455445)

// From where to pick packets
fd1::FromDevice($PORT1, SNIFFER false, METHOD LINUX, PROMISC true)
fd2::FromDevice($PORT2, SNIFFER false, METHOD LINUX, PROMISC true)

eth1_out:: AverageCounter
eth2_out:: AverageCounter
eth3_out:: AverageCounter

eth1_out_total:: Counter
eth2_out_total:: Counter
eth3_out_total:: Counter

eth1_in_total:: Counter
eth2_in_total:: Counter

eth1_in:: AverageCounter
eth2_in:: AverageCounter

arp_req_out:: Counter
arp_res_out:: Counter

arp_req_in:: Counter
arp_res_in:: Counter

service_in:: Counter
service_out:: Counter

icmp_counter:: Counter

discard_counter:: Counter

insp_counter:: Counter


// Where to send packets
td1::Queue -> eth1_out_total  -> eth1_out -> ToDevice($PORT1, METHOD LINUX)
td2::Queue -> eth2_out_total  -> eth2_out -> ToDevice($PORT2, METHOD LINUX)
td3::Queue -> eth3_out_total  -> eth3_out -> ToDevice($PORT3, METHOD LINUX)

eth_classifier, eth_classifier2 :: Classifier(12/0806 20/0001,12/0806 20/0002,
			 	      		12/0800,
			       			-);
icmp_classifier :: Classifier(09/01, //ICMP
				-); //TCP or HTTP


tcp_classifier :: Classifier(13/02,       //SYN
			13/12,       //SYN ACK
			13/10,       //ACK
			13/04,       //RST
			13/11,       //FIN ACK
			-);

http_classifier :: Classifier(0/504f5354,	// POST
			0/505554,		// PUT
			-);

injections_classifier :: Classifier(
			$INJ1,				//cat etc/passwd
                        $INJ2,				//cat /var/log/
                        $INJ3,		                //INSERT
                        $INJ4,          	        //UPDATE
                        $INJ5,		                //DELETE
                        -);						

// From IN to OUT
fd2 -> eth2_in_total -> eth2_in -> eth_classifier2;

eth_classifier2[0] -> arp_req_out -> td1;
eth_classifier2[1] -> arp_res_out -> td1;
eth_classifier2[2] -> service_in -> td1;
eth_classifier2[3] -> discard_counter -> Discard;

// FROM OUT TO IN
fd1 -> eth1_in_total -> eth1_in -> eth_classifier;

eth_classifier[0] -> arp_req_in -> td2;
eth_classifier[1] -> arp_res_in -> td2;
eth_classifier[3] -> td2;
eth_classifier[2]->Strip(14)->CheckIPHeader-> service_out -> icmp_classifier; //check if its ICMP

icmp_classifier[0]->Unstrip(14)-> icmp_counter -> td2;
icmp_classifier[1]->StripIPHeader->tcp_classifier; //if not ICMP and its TCP 

// TCP SIGNALING ALLOWED
tcp_classifier[0] -> Print("SYN") -> UnstripIPHeader->Unstrip(14)->td2;
tcp_classifier[1] -> Print("SYN ACK") -> UnstripIPHeader->Unstrip(14)->td2;
tcp_classifier[2] -> Print("ACK") -> UnstripIPHeader->Unstrip(14)->td2;
tcp_classifier[3] -> Print("RST") -> UnstripIPHeader->Unstrip(14)->td2;
tcp_classifier[4] -> Print("FIN ACK") -> UnstripIPHeader->Unstrip(14)->td2;
tcp_classifier[5] -> Print("Go to http")->StripTCPHeader->http_classifier;

http_classifier[0] -> Print("HTTP POST") -> UnstripTCPHeader->UnstripIPHeader->Unstrip(14)->td2;
http_classifier[1] -> Print("HTTP PUT") -> injections_classifier;
http_classifier[2] ->UnstripIPHeader->Unstrip(14)->td3 	// send other traffic to insp

// if injections found -> forward to inspector
injections_classifier[0] -> UnstripTCPHeader->UnstripIPHeader->Unstrip(14)-> insp_counter -> td3;
injections_classifier[1] -> UnstripTCPHeader->UnstripIPHeader->Unstrip(14)-> insp_counter -> td3;
injections_classifier[2] -> UnstripTCPHeader->UnstripIPHeader->Unstrip(14)-> insp_counter -> td3;
injections_classifier[3] -> UnstripTCPHeader->UnstripIPHeader->Unstrip(14)-> insp_counter -> td3;
injections_classifier[4] -> UnstripTCPHeader->UnstripIPHeader->Unstrip(14)-> insp_counter -> td3;

// NO INJECTION MATCH - FORWARD NORMAL HTTP PUT TRAFFIC
injections_classifier[5] -> UnstripTCPHeader->UnstripIPHeader->Unstrip(14)->td2

outrate :: Script(TYPE PASSIVE, return $(add $(eth1_out.rate) $(eth2_out.rate) $(eth3_out.rate)))
inrate :: Script(TYPE PASSIVE, return $(add $(eth1_in.rate) $(eth2_in.rate)))

total_packets_in :: Script(TYPE PASSIVE, return $(add $(eth1_in_total.count) $(eth2_in_total.count)))
total_packets_out :: Script(TYPE PASSIVE, return $(add $(eth1_out_total.count) $(eth2_out_total.count) $(eth3_out_total.count)))

arp_req_total :: Script(TYPE PASSIVE, return $(add $(arp_req_out.count) $(arp_req_in.count)))
arp_res_total :: Script(TYPE PASSIVE, return $(add $(arp_res_out.count) $(arp_res_in.count)))

service_total :: Script(TYPE PASSIVE, return $(add $(service_in.count) $(service_out.count)))



DriverManager(wait, print > ../../results/ids.report "
		=================== IDS Report =========================
                Input Packet rate (pps) :  $(inrate.run),
                Output Packet rate (pps) :  $(outrate.run),
                
                Total # of input packets :  $(total_packets_in.run),
                Total # of output packets : $(total_packets_out.run),
                
                Total # of ARP requests :  $(arp_req_total.run),
                Total # of ARP response :  $(arp_res_total.run),
                
                Total # of service packets : $(service_total.run),
                Total # of ICMP packets : $(icmp_counter.count),
               	Total # of dropped packets : $(discard_counter.count),
		Total # of packets sent to Inspector: $(insp_counter.count),
                =========================================",
                stop);
