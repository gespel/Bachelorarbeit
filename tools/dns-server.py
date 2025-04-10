import socket
from scapy.all import DNS, DNSQR, DNSRR
import logging

LISTEN_IP = "10.3.10.45"
LISTEN_PORT = 53
TARGET_DOMAINS = ["example.local.", "example.com.", "example.org.", "test.local."]
REPLY_IP = "10.3.10.43"

logging.basicConfig(level=logging.INFO)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((LISTEN_IP, LISTEN_PORT))

logging.info(f"DNS-Server läuft auf {LISTEN_IP}:{LISTEN_PORT} für {TARGET_DOMAINS}")

while True:
    data, addr = sock.recvfrom(512)
    dns = DNS(data)
    #logging.info(f"Paket erhalten von {addr}")
    if dns.opcode == 0 and dns.qr == 0 and dns.qdcount == 1:
        qname = dns[DNSQR].qname.decode()
        #logging.info(f"Anfrage: {qname} von {addr}")

        if qname in TARGET_DOMAINS:
            response = DNS(
                id=dns.id,
                qr=1,
                aa=1,
                qd=dns.qd,
                an=DNSRR(rrname=qname, ttl=60, type="A", rclass="IN", rdata="1.1.1.1")
            )

            sock.sendto(bytes(response), (REPLY_IP, 5353))
            logging.info(f"Antwort gesendet: {qname} -> 1.1.1.1")
        else:
            logging.info("Nicht die gewünschte Domain")
