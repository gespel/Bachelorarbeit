#!/usr/bin/env python3
"""
Compute time deltas from p1 (eth.src -> eth.dst) to the next p2 (eth.src -> eth.dst)
using PyShark (tshark backend). Results reported in microseconds (µs).
"""
import argparse
import math
import statistics
import sys
from typing import List

import pyshark


def grab_times(pcap: str, src_mac: str, dst_mac: str) -> List[float]:
    dfilter = f"eth.src=={src_mac} && eth.dst=={dst_mac}"
    cap = pyshark.FileCapture(
        pcap,
        display_filter=dfilter,
        only_summaries=False,
        keep_packets=False,
        use_json=True,
        include_raw=False,
    )
    times = []
    try:
        for pkt in cap:
            times.append(float(pkt.sniff_timestamp))
    finally:
        cap.close()
    times.sort()
    return times


def pair_deltas_many_to_one(t1: List[float], t2: List[float]) -> List[float]:
    deltas = []
    j = 0
    n2 = len(t2)
    for ti in t1:
        while j < n2 and t2[j] < ti:
            j += 1
        if j < n2:
            deltas.append(t2[j] - ti)
        else:
            break
    return deltas


def pair_deltas_one_to_one(t1: List[float], t2: List[float]) -> List[float]:
    deltas = []
    j = 0
    n2 = len(t2)
    for ti in t1:
        while j < n2 and t2[j] < ti:
            j += 1
        if j < n2:
            deltas.append(t2[j] - ti)
            j += 1
        else:
            break
    return deltas


def fmt_us(x: float) -> str:
    return f"{x:f}"  # one decimal µs precision


def main():
    ap = argparse.ArgumentParser(
        description="Compute avg/stddev time from p1 to next p2 (eth.src/dst) in µs using PyShark."
    )
    ap.add_argument("pcap", help="Input pcap/pcapng file")
    ap.add_argument("--p1-src", required=True, help="MAC src for packet type 1")
    ap.add_argument("--p1-dst", required=True, help="MAC dst for packet type 1")
    ap.add_argument("--p2-src", required=True, help="MAC src for packet type 2")
    ap.add_argument("--p2-dst", required=True, help="MAC dst for packet type 2")
    ap.add_argument("--one-to-one", action="store_true",
                    help="Enforce one-to-one sequential pairing.")
    args = ap.parse_args()

    try:
        t1 = grab_times(args.pcap, args.p1_src, args.p1_dst)
        t2 = grab_times(args.pcap, args.p2_src, args.p2_dst)
    except Exception as e:
        print(f"Error reading with PyShark/tshark: {e}", file=sys.stderr)
        sys.exit(2)

    if not t1 or not t2:
        print("No p1 or p2 packets found.")
        sys.exit(1)

    if args.one_to_one:
        deltas = pair_deltas_one_to_one(t1, t2)
    else:
        deltas = pair_deltas_many_to_one(t1, t2)

    if not deltas:
        print("No p1→p2 pairs found.")
        sys.exit(1)

    # Convert seconds to µs
    deltas_us = [d * 1e6 for d in deltas]

    n = len(deltas_us)
    avg = statistics.fmean(deltas_us)
    sd = statistics.stdev(deltas_us) if n >= 2 else float("nan")
    dmin, dmax = min(deltas_us), max(deltas_us)

    print(f"Pairs: {n}")
    print(f"Average (µs): {fmt_us(avg)}")
    print(f"Std dev (sample, µs): {fmt_us(sd) if not math.isnan(sd) else 'nan'}")
    print(f"Min: {fmt_us(dmin)}   Max: {fmt_us(dmax)}")


if __name__ == "__main__":
    main()

