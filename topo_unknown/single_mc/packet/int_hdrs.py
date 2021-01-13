from scapy.all import *

class LastSWId(Packet):
    fields_desc = [ ByteField("last_sw_id", 0)] 

class IntHeader(Packet):
    fields_desc = [ ByteField("int_total_num", 0)]

class IntData(Packet):
    fields_desc = [ ByteField("sw_id", 0),
                    ByteField("ingress_port", 0),
                    ByteField("egress_port", 0),
                    ByteField("rsvd0", 0),
                    BitField("ingress_global_timestamp", 0, 48),
                    BitField("egress_global_timestamp", 0, 48),
                    BitField("enq_timestamp", 0, 32),
                    ByteField("rsvd1", 0),
                    BitField("enq_qdepth", 0, 24),
                    BitField("deq_timedelta", 0, 32),
                    ByteField("rsvd2", 0),
                    BitField("deq_qdepth", 0, 24)]
    
    
