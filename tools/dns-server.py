import socket
from scapy.all import DNS, DNSQR, DNSRR
import logging

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 53
TARGET_DOMAINS = ["example.local.", "example.com.", "example.org.", "test.local."]
REPLY_IP = "192.168.1.101"

logging.basicConfig(level=logging.INFO)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((LISTEN_IP, LISTEN_PORT))

logging.info(f"DNS-Server läuft auf {LISTEN_IP}:{LISTEN_PORT} für {TARGET_DOMAINS}")

while True:
    data, addr = sock.recvfrom(512)
    dns = DNS(data)

    if dns.opcode == 0 and dns.qr == 0 and dns.qdcount == 1:
        qname = dns[DNSQR].qname.decode()
        logging.info(f"Anfrage: {qname} von {addr}")

        if qname in TARGET_DOMAINS:
            response = DNS(
                id=dns.id,
                qr=1,
                aa=1,
                qd=dns.qd,
                an=DNSRR(rrname=qname, ttl=60, type="A", rclass="IN", rdata=REPLY_IP)
            )

            sock.sendto(bytes(response), addr)
            logging.info(f"Antwort gesendet: {qname} -> {REPLY_IP}")
        else:
            logging.info("Nicht die gewünschte Domain")