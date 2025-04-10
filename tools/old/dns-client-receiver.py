import time
from scapy.all import sniff, DNS, UDP

INTERFACE = "enp24s0f0np0"

print(f"[Receiver] Warte auf DNS-Antwort auf Interface {INTERFACE} ...")
while True:
    pkt = sniff(iface=INTERFACE, filter="udp port 5353", timeout=2, count=1)

    t = time.perf_counter()
    if pkt:
        with open("rtt.txt", "a") as f:
            f.write(f"r-{t}\n")
        try:
            dns_resp = pkt[0][DNS]
        except Exception as e:
            print(f"Error {pkt}")
        print(f"[Receiver] Antwort empfangen: {dns_resp.an.rdata} | time: {t}")
