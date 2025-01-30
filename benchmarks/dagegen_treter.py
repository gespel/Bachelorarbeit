from scapy.all import Ether, IP, UDP, sendp
import time
import random

def generate_random_ip():
    return ".".join(str(random.randint(0, 255)) for _ in range(4))

def generate_random_mac():
    return ":".join(f"{random.randint(0, 255):02x}" for _ in range(6))

def packet_thread():
    p = Ether(src=generate_random_mac(), dst="c4:70:bd:a0:56:ac") / IP(src=generate_random_ip(), dst="10.3.10.50") / UDP(sport=1234, dport=80) 
    while True:
        sendp(p, iface="enp24s0f0np0")
        time.sleep(0.5)
