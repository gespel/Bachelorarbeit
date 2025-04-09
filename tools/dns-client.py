import time
import random
from scapy.all import DNS, DNSQR, Ether, IP, UDP, sendp, get_if_hwaddr, sniff

INTERFACE = "enp24s0f0np0"
TARGET_MAC = "c4:70:bd:a0:56:ac"
SOURCE_MAC = get_if_hwaddr(INTERFACE)
TARGET_IP = "10.3.10.45"
SOURCE_IP = "10.3.10.42"
TARGET_PORT = 53

QUERY_DOMAINS = ["example.local.", "example.org.", "test.local."]
NUM_MEASUREMENTS = 100000

def send_and_receive():
    domain = random.choice(QUERY_DOMAINS)
    transaction_id = random.randint(0, 0xFFFF)

    dns_request = DNS(id=transaction_id, rd=1, qd=DNSQR(qname=domain))

    ether = Ether(src=SOURCE_MAC, dst=TARGET_MAC)
    ip = IP(src=SOURCE_IP, dst=TARGET_IP)
    sport = random.randint(1024, 65535)
    udp = UDP(sport=sport, dport=TARGET_PORT)
    packet = ether / ip / udp / dns_request

    start = time.time()
    sendp(packet, iface=INTERFACE, verbose=0)

    response = sniff(
        iface=INTERFACE,
        filter="udp port 5353",
        timeout=2,
        count=1
    )

    if response:
        dns_resp = response[0][DNS]
        rtt_ms = (time.time() - start) * 1000
        assert dns_resp.id == transaction_id
        dns_resp = response[0][DNS]
        print(f"{domain} -> Antwort: {dns_resp.an.rdata} | RTT: {rtt_ms:.2f} ms")
        return rtt_ms
    else:
        print(f"{domain} -> Keine Antwort erhalten.")
        return None

all_rtts = []
for _ in range(NUM_MEASUREMENTS):
    rtt = send_and_receive()
    if rtt:
        all_rtts.append(rtt)
    time.sleep(1)

if all_rtts:
    print(f"Durchschnittliche RTT: {sum(all_rtts) / len(all_rtts):.2f} ms")
else:
    print("Keine gültigen Antworten erhalten.")
