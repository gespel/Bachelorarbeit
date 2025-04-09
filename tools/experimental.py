import time
import random
from threading import Thread
from queue import Queue, Empty
from scapy.all import (
    DNS, DNSQR, Ether, IP, UDP,
    sendp, sniff, get_if_hwaddr
)

INTERFACE = "enp24s0f0np0"
TARGET_MAC = "c4:70:bd:a0:56:ac"
SOURCE_MAC = get_if_hwaddr(INTERFACE)
TARGET_IP = "10.3.10.45"
SOURCE_IP = "10.3.10.42"
TARGET_PORT = 53

QUERY_DOMAINS = ["example.local.", "example.org.", "test.local."]
DNS_TXID = 0x1234
SPORT = 5353

response_queue = Queue()

def packet_callback(pkt):
    if DNS in pkt and pkt[UDP].sport == TARGET_PORT and pkt[UDP].dport == SPORT:
        response_queue.put(pkt)

def start_sniffer():
    sniff(iface=INTERFACE, filter="udp and src port 5353", prn=packet_callback, store=0)

def send_dns_request(domain):
    dns_request = DNS(id=DNS_TXID, rd=1, qd=DNSQR(qname=domain))
    ether = Ether(src=SOURCE_MAC, dst=TARGET_MAC)
    ip = IP(src=SOURCE_IP, dst=TARGET_IP)
    udp = UDP(sport=SPORT, dport=TARGET_PORT)
    packet = ether / ip / udp / dns_request

    sendp(packet, iface=INTERFACE, verbose=0)

if __name__ == "__main__":
    sniffer_thread = Thread(target=start_sniffer, daemon=True)
    sniffer_thread.start()

    while True:
        domain = random.choice(QUERY_DOMAINS)
        print(f"[Sender] Sende Anfrage für {domain}")
        start = time.time()
        send_dns_request(domain)

        try:
            pkt = response_queue.get(timeout=2)
            end = time.time()

            dns_resp = pkt[DNS]
            if dns_resp.an:
                rtt_ms = (end - start) * 1000
                print(f"[Empfangen] Antwort: {dns_resp.an.rdata} | RTT: {rtt_ms:.2f} ms")
            else:
                print("[Empfangen] Keine Antwortdaten im DNS enthalten.")
        except Empty:
            print("[Empfangen] Timeout – keine Antwort erhalten.")

        time.sleep(1)