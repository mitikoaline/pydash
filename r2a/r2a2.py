from r2a.ir2a import IR2A

class R2A2(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.qi = []

    def handle_xml_request(self, msg):
        self.send_down(msg)

    def handle_xml_response(self, msg):
        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass
