from scapy.all import Ether, sendp, sniff
import time

# --- Konfiguration ---
iface = "enp24s0f0np0"          # Interface, über das du sendest
dst_mac = "a0:88:c2:b6:14:1a"   # MAC-Adresse des XDP-Knotens
src_mac = "08:c0:eb:a5:61:26"   # Deine eigene MAC
payload = b"x"                   # Beliebiger Payload

# --- Paket bauen ---
pkt = Ether(src=src_mac, dst=dst_mac) / payload

# --- Funktion zum Sniffen der Rückkehr ---
def wait_for_reply(timeout=2):
    # Filter: Pakete, die an deine MAC zurückgehen
    filter_func = lambda p: Ether in p and p[Ether].dst.lower() == src_mac.lower()
    packets = sniff(iface=iface, lfilter=filter_func, timeout=timeout)
    return packets

# --- Test senden & RTT messen ---
send_time = time.time()
sendp(pkt, iface=iface, verbose=False)

replies = wait_for_reply(timeout=2)
recv_time = time.time()

if replies:
    rtt = (recv_time - send_time) * 1000  # in ms
    print(f"Packet returned! RTT ≈ {rtt:.3f} ms")
else:
    print("No reply within timeout")
