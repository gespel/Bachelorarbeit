from scapy.all import Ether, IP, UDP, sendp

p = Ether(src="aa:aa:aa:aa:aa:aa", dst="c4:70:bd:a0:56:ac") / IP(src="8.8.8.8", dst="1.2.3.4") / UDP(sport=1234, dport= 1234) 

sendp(p)
