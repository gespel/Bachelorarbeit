import socket
import time
import random
from scapy.all import DNS, DNSQR, Ether, IP, UDP, sendp, get_if_hwaddr

INTERFACE = "enp24s0f0np0"
TARGET_MAC = "c4:70:bd:a0:56:ac"
SOURCE_MAC = get_if_hwaddr(INTERFACE)
TARGET_IP = "10.3.10.45"
SOURCE_IP = "10.3.10.42"
TARGET_PORT = 53

QUERY_DOMAINS = ["example.local.", "example.org.", "test.local."]
NUM_MEASUREMENTS = 1000

def send_and_receive():
    domain = random.choice(QUERY_DOMAINS)
    transaction_id = random.randint(0, 0xFFFF)
    sport = random.randint(1024, 65535)

    dns_request = DNS(id=transaction_id, rd=1, qd=DNSQR(qname=domain))

    ether = Ether(src=SOURCE_MAC, dst=TARGET_MAC)
    ip = IP(src=SOURCE_IP, dst=TARGET_IP)
    udp = UDP(sport=sport, dport=TARGET_PORT)
    packet = ether / ip / udp / dns_request

    # UDP-Socket für Empfang öffnen
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recv_sock.bind((SOURCE_IP, sport))
    recv_sock.settimeout(2)

    start = time.time()
    sendp(packet, iface=INTERFACE, verbose=0)

    try:
        data, addr = recv_sock.recvfrom(512)
        rtt_ms = (time.time() - start) * 1000

        dns_resp = DNS(data)
        if dns_resp.id != transaction_id:
            print(f"Transaction ID stimmt nicht: {dns_resp.id} != {transaction_id}")
            return None

        if dns_resp.an:
            print(f"{domain} -> Antwort: {dns_resp.an.rdata} | RTT: {rtt_ms:.2f} ms")
        else:
            print(f"{domain} -> Leere Antwort | RTT: {rtt_ms:.2f} ms")

        return rtt_ms

    except socket.timeout:
        print(f"{domain} -> Timeout")
        return None

    finally:
        recv_sock.close()


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
