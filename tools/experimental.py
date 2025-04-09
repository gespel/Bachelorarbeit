import time
import random
from scapy.all import (
    DNS, DNSQR, DNSRR,
    Ether, IP, UDP,
    sendp, sniff, get_if_hwaddr
)

INTERFACE = "enp24s0f0np0"
TARGET_MAC = "c4:70:bd:a0:56:ac"
SOURCE_MAC = get_if_hwaddr(INTERFACE)
TARGET_IP = "10.3.10.45"
SOURCE_IP = "10.3.10.42"
TARGET_PORT = 53

QUERY_DOMAINS = ["example.local.", "example.org.", "test.local."]

DNS_TXID = 0x1234  # feste ID
SPORT = 44444      # feste Source-Port

def send_dns_request(domain):
    dns_request = DNS(id=DNS_TXID, rd=1, qd=DNSQR(qname=domain))
    ether = Ether(src=SOURCE_MAC, dst=TARGET_MAC)
    ip = IP(src=SOURCE_IP, dst=TARGET_IP)
    udp = UDP(sport=SPORT, dport=TARGET_PORT)
    packet = ether / ip / udp / dns_request

    sendp(packet, iface=INTERFACE, verbose=0)

def wait_for_response(timeout=2):
    pkt = sniff(
        iface=INTERFACE,
        filter=f"udp and port {SPORT}",
        timeout=timeout,
        count=1
    )
    return pkt[0] if pkt else None

if __name__ == "__main__":
    while True:
        domain = random.choice(QUERY_DOMAINS)
        print(f"[Sender] Sende Anfrage für {domain}")
        start = time.time()
        send_dns_request(domain)

        pkt = wait_for_response(timeout=2)
        end = time.time()

        if pkt and DNS in pkt:
            dns_resp = pkt[DNS]
            if dns_resp.an:
                rtt_ms = (end - start) * 1000
                print(f"[Empfangen] Antwort: {dns_resp.an.rdata} | RTT: {rtt_ms:.2f} ms")
            else:
                print("[Empfangen] Keine Antwortdaten im DNS enthalten.")
        else:
            print("[Empfangen] Keine Antwort empfangen.")

        time.sleep(1)