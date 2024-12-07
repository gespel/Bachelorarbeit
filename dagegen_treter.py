from scapy.all import Ether, IP, UDP, sendp
import time

p = Ether(src="aa:aa:aa:aa:aa:aa", dst="c4:70:bd:a0:56:ac") / IP(src="8.8.8.8", dst="10.3.10.50") / UDP(sport=1234, dport= 1234) 

while True:
    sendp(p, iface="eno8303")
    time.sleep(0.5)
