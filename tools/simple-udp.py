from scapy.all import Ether, IP, UDP, sendp, Raw

#dst_mac = "c4:70:bd:a0:56:ac"   # MAC-Adresse des Empfängers
dst_mac = "a0:88:c2:b6:14:1a"
src_mac = "08:c0:eb:a5:61:26"   # deine Quell-MAC (z.B. Interface-MAC)
dst_ip = "192.168.1.100"        # Ziel-IP (muss zum Empfänger passen)
src_ip = "192.168.1.10"         # deine Quell-IP
dst_port = 5005                 # UDP-Port beim Empfänger
src_port = 12345                # UDP-Quell-Port
payload = b"x"

pkt = (
    Ether(dst=dst_mac, src=src_mac) /
    IP(dst=dst_ip, src=src_ip) /
    UDP(dport=dst_port, sport=src_port) /
    Raw(load=payload)
)

# Paket über ein bestimmtes Interface senden
import time
while True:
	sendp(pkt, iface="enp24s0f0np0", verbose=True)
	time.sleep(1)
