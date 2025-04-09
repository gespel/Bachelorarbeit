import time
from scapy.all import sniff, DNS, UDP

INTERFACE = "enp24s0f0np0"

print(f"[Receiver] Warte auf DNS-Antwort auf Interface {INTERFACE} ...")
while True:
    pkt = sniff(iface=INTERFACE, filter="udp port 5353", timeout=2, count=1)


    t = time.time()
    with open("rtt.txt", "a") as f:
        f.write("r-" + str(t))
    dns_resp = pkt[0][DNS]
    print(f"[Receiver] Antwort empfangen: {dns_resp.an.rdata} | time: {t}")
