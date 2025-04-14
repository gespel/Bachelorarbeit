import time
import random
import tqdm
from scapy.all import DNS, DNSQR, Ether, IP, UDP, sendp, get_if_hwaddr

INTERFACE = "enp24s0f0np0"
TARGET_MAC = "c4:70:bd:a0:56:ac"
SOURCE_MAC = get_if_hwaddr(INTERFACE)
TARGET_IP = "10.3.10.45"
SOURCE_IP = "10.3.10.42"
TARGET_PORT = 53

QUERY_DOMAINS = ["example.local.", "example.org.", "test.local."]

DNS_TXID = 0x1234  # feste ID
SPORT = 44444      # feste Source-Port für einfaches Matchen

def send_dns_request(domain):
    dns_request = DNS(id=DNS_TXID, rd=1, qd=DNSQR(qname=domain))
    ether = Ether(src=SOURCE_MAC, dst=TARGET_MAC)
    ip = IP(src=SOURCE_IP, dst=TARGET_IP)
    udp = UDP(sport=SPORT, dport=TARGET_PORT)
    packet = ether / ip / udp / dns_request
    sendp(packet, iface=INTERFACE, verbose=0)
    out = time.perf_counter()
    return out

if __name__ == "__main__":
    for i in tqdm.tqdm(range(1800*int(sys.argv[1]))):
        domain = random.choice(QUERY_DOMAINS)
        start = send_dns_request(domain)
        
        #print(f"Nr. {i} [Sender] Sende Anfrage für {domain} | time: {start}")
        time.sleep(1/int(sys.argv[1]))
        