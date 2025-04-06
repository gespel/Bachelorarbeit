import argparse
import os
from trex_stl_lib.api import *

SRC_IP = "10.0.0.1"
DEST_IP = "10.0.0.1"
DEST_PORT = 80
SRC_PORT = 1234
VALID_IP_RANGE = "1.1.1.2", "1.1.1.2"
bench_pps = 120000000
default_pkt_size = 64  # Default Packet Size

class STLS1(object):
    def __init__(self):
        pass

    def create_stream1(self, pps, pkt_size):
        # Ethernet(14) + IP(20) + UDP(8) = 42 bytes
        header_size = 14 + 20 + 8
        payload_size = max(pkt_size - header_size, 0)

        # Erzeuge Payload mit 'x'
        payload = "x" * payload_size

        pkt = Ether() / IP(src=SRC_IP, dst=DEST_IP, id=1, tos=0) / UDP(sport=SRC_PORT, dport=DEST_PORT) / payload.encode("ascii")

        vm = STLScVmRaw([
            STLVmFlowVar("ip_src", min_value=VALID_IP_RANGE[0], max_value=VALID_IP_RANGE[1], size=4, step=1, op="inc"),
            STLVmWrFlowVar(fv_name="ip_src", pkt_offset="IP.src"),
            STLVmFixChecksumHw(l3_offset="IP", l4_offset="UDP", l4_type=CTRexVmInsFixHwCs.L4_TYPE_UDP)
        ], cache_size=254)

        return STLStream(
            packet=STLPktBuilder(pkt=pkt, vm=vm),
            mode=STLTXCont(pps=pps),
            flow_stats=STLFlowStats(pg_id=1)
        )

    def get_streams(self, tunables, **kwargs):
        parser = argparse.ArgumentParser(
            description='Argparser for {}'.format(os.path.basename(__file__)),
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        parser.add_argument('--ppsv', type=int, default=bench_pps, help="Packets per second for valid traffic")
        parser.add_argument('--pkt_size', type=int, default=default_pkt_size, help="Total packet size (bytes, incl. headers)")

        args = parser.parse_args(tunables)
        return [self.create_stream1(args.ppsv, args.pkt_size)]

def register():
    return STLS1()