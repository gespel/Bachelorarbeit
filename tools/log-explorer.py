from datetime import datetime
import sys

logfile = sys.argv[1]

time_format = "%H:%M:%S.%f"

rtts = []
lost = 0

with open(logfile, "r") as f:
    lines = [line.strip() for line in f if line.strip()]

i = 0
while i < len(lines):
    line = lines[i]
    
    if "4660+" in line:
        request_time = datetime.strptime(line.split()[0], time_format)
        
        if i + 1 < len(lines):
            next_line = lines[i + 1]
            if "4660*-" in next_line:
                response_time = datetime.strptime(next_line.split()[0], time_format)
                rtt = (response_time - request_time).total_seconds() * 1000
                if rtt < 1000:
                    rtts.append(rtt)
                i += 2
                continue
        
        lost += 1
        i += 1
    else:
        i += 1  # Skip non-request lines

total_requests = len(rtts) + lost

for idx, rtt in enumerate(rtts, 1):
    print(f"RTT #{idx}: {rtt:.3f} ms")

if rtts:
    avg_rtt = sum(rtts) / len(rtts)
    print(f"\nDurchschnittliche RTT: {avg_rtt:.6f} ms")

print(f"\nAnzahl Anfragen insgesamt: {total_requests}")
print(f"Erfolgreiche Antworten: {len(rtts)}")
print(f"Verlorene Pakete (keine Antwort): {lost}")
print(f"Packetloss: {lost/total_requests*100} %")
