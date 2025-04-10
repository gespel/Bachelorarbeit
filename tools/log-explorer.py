from datetime import datetime
import sys

logfile = sys.argv[1]

time_format = "%H:%M:%S.%f"

requests = []
responses = []

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

used_responses = set()
matched_pairs = []

for req_time in requests:
    pair = None
    for i, resp_time in enumerate(responses):
        if i in used_responses:
            continue
        if resp_time > req_time:
            pair = (req_time, resp_time)
            used_responses.add(i)
            break
    if pair:
        matched_pairs.append(pair)

rtts = [(resp - req).total_seconds() * 1000 for req, resp in matched_pairs]  # in ms

total_requests = len(requests)
successful = len(matched_pairs)
lost = total_requests - successful

for i, rtt in enumerate(rtts, 1):
    print(f"RTT #{i}: {rtt:.3f} ms")

if rtts:
    avg_rtt = sum(rtts) / len(rtts)
    print(f"\nDurchschnittliche RTT: {avg_rtt:.3f} ms")

print(f"\nAnzahl Anfragen insgesamt: {total_requests}")
print(f"Erfolgreiche Antworten: {successful}")
print(f"Verlorene Pakete (keine Antwort): {lost}")