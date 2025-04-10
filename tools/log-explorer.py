from datetime import datetime
import sys

logfile = sys.argv[1]

requests = []
responses = []

time_format = "%H:%M:%S.%f"

with open(logfile, "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        timestamp = line.split()[0]
        if "4660+" in line:
            requests.append(datetime.strptime(timestamp, time_format))
        elif "4660*-" in line:
            responses.append(datetime.strptime(timestamp, time_format))

rtts = []
paired_count = min(len(requests), len(responses))

for i in range(paired_count):
    rtt = (responses[i] - requests[i]).total_seconds() * 1000
    rtts.append(rtt)

lost_requests = len(requests) - paired_count
successful_requests = paired_count
total_requests = len(requests)

for i, rtt in enumerate(rtts, 1):
    print(f"RTT #{i}: {rtt:.3f} ms")

if rtts:
    avg_rtt = sum(rtts) / len(rtts)
    print(f"\nDurchschnittliche RTT: {avg_rtt:.3f} ms")

print(f"\nAnzahl Anfragen insgesamt: {total_requests}")
print(f"Erfolgreiche Antworten: {successful_requests}")
print(f"Verlorene Pakete (keine Antwort): {lost_requests}")