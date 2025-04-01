from scapy.all import *
import time

dst_mac = "AA:BB:CC:DD:EE:FF"   # Ziel-MAC-Adresse
src_mac = "11:22:33:44:55:66"   # Eigene MAC-Adresse
dst_ip = "192.168.1.100"        # Ziel-IP-Adresse
src_ip = "192.168.1.200"        # Eigene IP-Adresse
dst_port = 5201                 # Ziel-Port (sollte geschlossen sein)
iface = "eth0"                  # Netzwerkinterface

eth = Ether(dst=dst_mac, src=src_mac)
ip = IP(dst=dst_ip, src=src_ip)
udp = UDP(dport=dst_port, sport=12345)
payload = b"TEST"
pkt = eth / ip / udp / payload

send_time = time.time()
ans = srp1(pkt, iface=iface, timeout=2, verbose=False)

if ans:
    recv_time = time.time()
    rtt = (recv_time - send_time) * 1000  # in ms
    print(f"Latenz: {rtt:.3f} ms")
else:
    print("Keine Antwort erhalten.")
