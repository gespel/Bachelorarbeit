from scapy.all import Ether, IP, UDP, DNS, DNSQR, sendp
from tqdm import tqdm
import time
import sys

# MAC-Adressen
dst_mac = "c4:70:bd:a0:56:ac" # bluefield
# dst_mac = "a0:88:c2:b6:14:1a" # fips1
#dst_mac = "a0:88:c2:b5:f4:5a" # fips2
# dst_mac = "c4:70:bd:a0:56:ac"  # aktuell verwendete Ziel-MAC
src_mac = "a0:88:c2:b6:14:1a"   # deine Quell-MAC

# IP-Adressen und Ports
src_ip = "1.2.3.4"
dst_ip = "10.3.10.45"
src_port = 12345
dst_port = 53  # DNS-Port

# DNS-Anfrage
dns_name = "example.com"

# Paket erstellen
pkt = (
    Ether(src=src_mac, dst=dst_mac) /
    IP(src=src_ip, dst=dst_ip) /
    UDP(sport=src_port, dport=dst_port) /
    DNS(rd=1, qd=DNSQR(qname=dns_name))
)

# Sendeparameter
duration_sec = 3 * 60     # 3 Minuten
interval = 0.2            # 0,2 Sekunden

# Berechne Anzahl der Pakete
num_packets = int(duration_sec / interval)

if "--infinite" in sys.argv:
    while True:
        sendp(pkt, iface="enp24s0f0np0", verbose=False)
        time.sleep(interval)
else:
# Pakete mit Fortschrittsbalken senden
    for _ in tqdm(range(num_packets), desc="Sende DNS-Pakete"):
        sendp(pkt, iface="enp24s0f0np0", verbose=False)
        time.sleep(interval)
