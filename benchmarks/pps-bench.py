import argparse

from trex_stl_lib.api import *

SRC_IP = "10.0.0.1"
DEST_IP = "10.0.0.1"
DEST_PORT = 80
SRC_PORT = 1234
#VALID_IP_RANGE = "10.3.11.1","10.3.11.254"
#VALID_IP_RANGE = "10.0.0.2","10.0.0.2"
VALID_IP_RANGE = "1.1.1.2", "1.1.1.2"
bench_pps = 120000000


class STLS1(object):
    def __init__ (self):
        pass
    def create_stream1 (self,pps):
        payload = ""
        # Ethernet(14) + IP(20) + UDP(8) = 42 bytes
        for x in range(0, 22):
            payload += "x"
        pkt =  Ether()/IP(src=SRC_IP,dst=DEST_IP,id=1,tos=0)/UDP(sport=SRC_PORT,dport=DEST_PORT)/(payload.encode("ascii"))
        vm = STLScVmRaw([STLVmFlowVar("ip_src", min_value=VALID_IP_RANGE[0],max_value=VALID_IP_RANGE[1], size=4, step=1,op="inc"),
             STLVmWrFlowVar(fv_name="ip_src", pkt_offset= "IP.src"),
             STLVmFixChecksumHw(l3_offset="IP",l4_offset="UDP",l4_type=CTRexVmInsFixHwCs.L4_TYPE_UDP)],
             cache_size = 254

        )
        return STLStream(packet = STLPktBuilder(pkt = pkt ,vm = vm),
               mode = STLTXCont(pps = pps),
               flow_stats = STLFlowStats(pg_id = 1))

    def get_streams (self,tunables,**kwargs):
        parser = argparse.ArgumentParser(description='Argparser for {}'.format(os.path.basename(__file__)),
                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--ppsv',type=int,default=bench_pps,
               help="Packets per second for valid traffic")

        args = parser.parse_args(tunables)
        return [self.create_stream1(args.ppsv)]
        #return [self.create_stream1(args.ppsv),self.create_stream2(args.ppsi)]
def register():
    return STLS1()