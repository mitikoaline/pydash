from r2a.ir2a import IR2A
from player.parser import *
import time
import math

class R2A2(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.parsed_mpd = ''
        self.qi = []

        self.segment_throughput = []
        self.estimated_throughput = []
        self.request_time = 0
        self.p = 0


    def handle_xml_request(self, msg):
        # faz a requisicao MPD
        self.send_down(msg)

    def handle_xml_response(self, msg):
        self.parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = self.parsed_mpd.get_qi()
        self.send_up(msg)



    def handle_segment_size_request(self, msg):

        self.request_time = time.perf_counter()

        # verificar valores de Po, k, mi
        Po = 0.2
        k = 21 
        mi = 0.5

        if self.estimated_throughput:
            if len(self.estimated_throughput) < 3:

                # Te(i) = Ts(i - 1) , para i = 1, 2
                self.estimated_throughput.append(self.segment_throughput[-1])
        
            else:
                # delta = 1 / (1 + e^(-k(p - Po)))
                delta = 1 / (1 + math.pow(math.e, -k * (self.p - Po)))

                # Te(i) = (1 - delta).Te(i - 2) + delta.Ts(i - 1) , para i > 0
                te = (1 - delta) * self.estimated_throughput[-2] + delta * self.segment_throughput[-1]
                self.estimated_throughput.append(te)

            # Rc(i) = (1 - mi).Te(i)
            bitrate_constraint = (1 - mi) * self.estimated_throughput[-1]

            for i in self.qi:
                if bitrate_constraint > i:
                    sel_qi = i

        else:
            # Te(0) pega a menor taxa disponivel
            self.estimated_throughput.append(self.qi[0])
            sel_qi = self.qi[0]

        msg.add_quality_id(sel_qi)
        self.send_down(msg)





    def handle_segment_size_response(self, msg):
        t = time.perf_counter() - self.request_time
        self.segment_throughput.append(msg.get_bit_length() / t)

        if self.estimated_throughput:

            # p = |Ts(i) - Te(i)| / Te(i)
            self.p = abs(self.segment_throughput[-1] - self.estimated_throughput[-1]) / self.estimated_throughput[-1]

        self.send_up(msg)

        print("--------------------------------------------------------------------------------")


    def initialize(self):
        pass

    def finalization(self):
        pass
