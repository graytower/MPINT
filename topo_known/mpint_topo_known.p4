/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

/*************************************************************************
*********************** C O N S T A N T S ********************************
*************************************************************************/
#define MAX_HOPS 20
#define ETHER_TYPE_MPINT 0x2020

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/
typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>  version;
    bit<4>  ihl;
    bit<8>  diffserv;
    bit<16> totalLen;
    bit<16> identification;
    bit<3>  flags;
    bit<13> fragOffset;
    bit<8>  ttl;
    bit<8>  protocol;
    bit<16> hdrChecksum;
    bit<32> srcAddr;
    bit<32> dstAddr;
}

header intoption_t {
    bit<8>    int_total_num;         
}

header inthdr_t {
    bit<8>    sw_id;
    bit<8>    ingress_port;
    bit<8>    egress_port;
    bit<8>    replicate_count;
    bit<48>   ingress_global_timestamp;
    bit<48>   egress_global_timestamp;
    bit<32>   enq_timestamp;
    bit<8>    rsvd1;
    bit<24>   enq_qdepth;
    bit<32>   deq_timedelta;
    bit<8>    rsvd2;
    bit<24>   deq_qdepth;
}

header last_egress_sampling_timestamp_t {
    bit<48>   h_last_egress_sampling_timestamp;
}

struct metadata {
    bit<8> int_info_remaining;
    last_egress_sampling_timestamp_t m_last_egress_sampling_timestamp;
}

struct headers {
    ethernet_t         ethernet;
	//ipv4_t             ipv4;
	intoption_t        int_option;
	inthdr_t[MAX_HOPS] int_info;
}

register<bit<48>>(960) r_last_egress_global_timestamp;

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/
parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }
	
	state parse_ethernet {
	    packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            //ETHER_TYPE_MPINT: parse_ipv4;
            ETHER_TYPE_MPINT: parse_int_option;
            //default: accept;
        }
	}
	
	//state parse_ipv4 {
	//    packet.extract(hdr.ipv4);
	//	transition parse_int_option;
	//}
	
	state parse_int_option {
	    packet.extract(hdr.int_option);
		meta.int_info_remaining = hdr.int_option.int_total_num;
        transition select(meta.int_info_remaining) {
            0 : accept;
            default: parse_int_info;
        }
	}
	
	state parse_int_info {
	    packet.extract(hdr.int_info.next);
		meta.int_info_remaining = meta.int_info_remaining - 1;
		transition select(meta.int_info_remaining) {
            0 : accept;
            default: parse_int_info;
        }
	}
}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/
control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/
control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action multicast() {
        standard_metadata.mcast_grp = 1;
    }

    table ethertype_check_for_mc {
        key = {
            hdr.ethernet.etherType : exact;
        }
        actions = {
            multicast;
            drop;
        }
        size = 1024;
        default_action = drop;
    }
    apply {
        if (hdr.ethernet.isValid())
            ethertype_check_for_mc.apply();
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/
control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {

    action drop() {
        mark_to_drop(standard_metadata);
    }
    
    action add_int_info(bit<8> sw_id, bit<8> rep_count) { 
        hdr.int_option.int_total_num = hdr.int_option.int_total_num + 1;
        hdr.int_info.push_front(1);
        hdr.int_info[0].setValid();
		hdr.int_info[0].sw_id = (bit<8>)sw_id;
        hdr.int_info[0].ingress_port=(bit<8>)standard_metadata.ingress_port;
        hdr.int_info[0].egress_port=(bit<8>)standard_metadata.egress_port;
        hdr.int_info[0].replicate_count=(bit<8>)rep_count;
        hdr.int_info[0].ingress_global_timestamp=(bit<48>)standard_metadata.ingress_global_timestamp;
        hdr.int_info[0].egress_global_timestamp=(bit<48>)standard_metadata.egress_global_timestamp;
        hdr.int_info[0].enq_timestamp=(bit<32>)standard_metadata.enq_timestamp;
        hdr.int_info[0].enq_qdepth=(bit<24>)standard_metadata.enq_qdepth;
        hdr.int_info[0].deq_timedelta=(bit<32>)standard_metadata.deq_timedelta;
        hdr.int_info[0].deq_qdepth=(bit<24>)standard_metadata.deq_qdepth;
    }
    
    action del_int_info() {
        hdr.int_option.int_total_num = 0;
        hdr.int_info.pop_front(MAX_HOPS);
    }
    
    table addIntInfo {
        key = {
            hdr.ethernet.etherType : exact;
            standard_metadata.mcast_grp : exact;
        }
        actions = { 
	        add_int_info; 
	        NoAction; 
        }
        default_action = NoAction();      
    }
    
    table delIntInfo {
        key = {
            hdr.ethernet.etherType : exact;
        }
        actions = { 
	        del_int_info; 
	        NoAction; 
        }
        default_action = NoAction();      
    }
    
    apply {
        // Prune multicast packet to ingress port to preventing loop
        if (standard_metadata.egress_port == standard_metadata.ingress_port) {
            drop();
        }
        else {        
            if (hdr.int_option.isValid()) {
                r_last_egress_global_timestamp.read(meta.m_last_egress_sampling_timestamp.h_last_egress_sampling_timestamp, 
                                                   (bit<32>)standard_metadata.egress_port);
                
                    if (standard_metadata.egress_rid == 1){
                        if(standard_metadata.egress_global_timestamp - meta.m_last_egress_sampling_timestamp.h_last_egress_sampling_timestamp > 50000) {

                            addIntInfo.apply();
                            r_last_egress_global_timestamp.write((bit<32>)standard_metadata.egress_port, standard_metadata.egress_global_timestamp);
                        }
                    }
                    else {
                        delIntInfo.apply();
                    }
            }
        }
    }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/
control MyComputeChecksum(inout headers hdr, inout metadata meta) {
     apply {
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/
control MyDeparser(packet_out packet, in headers hdr) {
    apply {
	    packet.emit(hdr.ethernet);
        //packet.emit(hdr.ipv4);
        packet.emit(hdr.int_option);
        packet.emit(hdr.int_info);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/
V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
