import argparse
import os
from trex_stl_lib.api import *

SRC_PORT = 1234
DEST_IP = "10.0.0.1"
DEST_PORT = 80
SRC_IP_LIST = ["10.2.11.2", "10.2.11.3", "10.2.11.4", "10.2.11.5"]
bench_pps = 120000000


class STLS1(object):
    def __init__(self):
        pass

    def create_stream_with_ip(self, pps, src_ip, pg_id):
        payload = "x" * 86  # Ethernet(14) + IP(20) + UDP(8) = 42 bytes

        pkt = Ether() / IP(src=src_ip, dst=DEST_IP, id=1, tos=0) / UDP(sport=SRC_PORT, dport=DEST_PORT) / payload.encode("ascii")

        vm = STLScVmRaw([
            STLVmFixChecksumHw(l3_offset="IP", l4_offset="UDP", l4_type=CTRexVmInsFixHwCs.L4_TYPE_UDP)
        ])

        return STLStream(packet=STLPktBuilder(pkt=pkt, vm=vm),
                         mode=STLTXCont(pps=pps),
                         flow_stats=STLFlowStats(pg_id=pg_id))

    def get_streams(self, tunables, **kwargs):
        parser = argparse.ArgumentParser(description='Argparser for {}'.format(os.path.basename(__file__)),
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--ppsv', type=int, default=bench_pps,
                            help="Packets per second for valid traffic")

        args = parser.parse_args(tunables)

        streams = []
        pps_per_stream = args.ppsv // len(SRC_IP_LIST)

        for i, src_ip in enumerate(SRC_IP_LIST):
            streams.append(self.create_stream_with_ip(pps=pps_per_stream, src_ip=src_ip, pg_id=i + 1))

        return streams


def register():
    return STLS1()