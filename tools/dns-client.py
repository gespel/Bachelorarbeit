import socket
import time
import random
from scapy.all import DNS, DNSQR


SERVER_IP = "127.0.0.1"
SERVER_PORT = 53
QUERY_DOMAINS = ["example.local.", "example.org.", "test.local."]
NUM_MEASUREMENTS = 10

def send_request():
    domain = QUERY_DOMAINS[random.randint(0, 2)]
    dns_request = DNS(id=0xAAAA, rd=1, qd=DNSQR(qname=domain))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)

    try:
        start = time.time()
        sock.sendto(bytes(dns_request), (SERVER_IP, SERVER_PORT))

        response, _ = sock.recvfrom(512)
        end = time.time()

        rtt_ms = (end - start) * 1000

        dns_resp = DNS(response)
        if dns_resp.an:
            print(f"{domain} -> Antwortdaten: {dns_resp.an.rdata} Latenz: {rtt_ms:.2f} ms")
        else:
            print("Keine Antwortdaten im Paket.")

    except socket.timeout:
        print("Zeitüberschreitung – keine Antwort vom Server.")
    finally:
        sock.close()
        return rtt_ms

meanmean = 0
latency = []

for j in range(NUM_MEASUREMENTS):
    for i in range(100):
        latency.append(send_request())

    mean = 0
    for l in latency:
        mean += l
    mean /= len(latency)
    meanmean += mean
    time.sleep(3)

meanmean /= NUM_MEASUREMENTS

print(f"Durchschnittslatenz: {mean:.4f} ms")