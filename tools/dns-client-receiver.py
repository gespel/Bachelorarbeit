import time
from scapy.all import sniff, DNS, UDP

INTERFACE = "enp24s0f0np0"
SPORT = 5353 

def match_packet(pkt):
    return (
        pkt.haslayer(DNS)
        and pkt.haslayer(UDP)
        and pkt[DNS].qr == 1
        and pkt[UDP].dport == SPORT
    )

print(f"[Receiver] Warte auf DNS-Antwort auf Interface {INTERFACE} ...")
while True:
    pkt = sniff(iface=INTERFACE, lfilter=match_packet, timeout=2, count=1)

    if pkt:
        #rtt_ms = (time.time() - sent_time) * 1000
        dns_resp = pkt[0][DNS]
        print(f"[Receiver] Antwort empfangen: {dns_resp.an.rdata} | time: {time.time()}")
    else:
        print("[Receiver] Keine Antwort empfangen.")