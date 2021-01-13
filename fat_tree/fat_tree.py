#!/usr/bin/env python

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.cli import CLI

from p4_mininet import P4Switch, P4Host

import argparse
from time import sleep

parser = argparse.ArgumentParser(description='MPINT')
parser.add_argument('--behavioral-exe', help='Path to behavioral executable',
                    type=str, action="store", default="/home/zyan/mininet/behavioral-model/"
                                                      "targets/simple_switch/simple_switch")
parser.add_argument('--thrift-port', help='Thrift server port for table updates',
                    type=int, action="store", default=9090)
parser.add_argument('--density', help='Number of hosts to connect to each edge layer switch',
                    type=int, action="store", default=2)
parser.add_argument('--pod-num', help='Number of pods in fat tree network',
                    type=int, action="store", default=4)
parser.add_argument('--json', help='Path to JSON config file',
                    type=str, action="store", required=True)
parser.add_argument('--pcap-dump', help='Dump packets on interfaces to pcap files',
                    type=str, action="store", required=False, default=False)

args = parser.parse_args()


class FatTree(Topo):
    """Init Fat Tree Topology"""
    core_switch_list = []
    aggregation_switch_list = []
    edge_switch_list = []
    host_list = []
    core_switch_num = 0
    aggregation_switch_num = 0
    edge_switch_num = 0
    host_num = 0
    pod_num = 0
    density = 0

    def __init__(self, sw_path, json_path, thrift_port, pcap_dump, pod_num, density, **opts):
        self.core_switch_num = (pod_num / 2) ** 2
        self.aggregation_switch_num = pod_num * pod_num / 2
        self.edge_switch_num = pod_num * pod_num / 2
        self.host_num = self.edge_switch_num * density
        self.pod_num = pod_num
        self.density = density

        Topo.__init__(self, **opts)
        self.create_fat_tree_topology(sw_path, json_path, thrift_port, pcap_dump)

    def create_fat_tree_topology(self, sw_path, json_path, thrift_port, pcap_dump):
        self.create_core_switch(sw_path, json_path, thrift_port, pcap_dump)
        current_thrift_port = thrift_port + self.core_switch_num

        self.create_aggregation_switch(sw_path, json_path, current_thrift_port, pcap_dump)
        current_thrift_port = current_thrift_port + self.aggregation_switch_num

        self.create_edge_switch(sw_path, json_path, current_thrift_port, pcap_dump)

        self.create_host()

        self.create_link()

    def create_core_switch(self, sw_path, json_path, thrift_port, pcap_dump):
        for i in xrange(self.core_switch_num):
            sw = self.addSwitch('c%d' % i, sw_path=sw_path, json_path=json_path,
                                thrift_port=thrift_port, pcap_dump=pcap_dump)
            self.core_switch_list.append(sw)
            thrift_port += 1

    def create_aggregation_switch(self, sw_path, json_path, thrift_port, pcap_dump):
        for i in xrange(self.aggregation_switch_num):
            sw = self.addSwitch('a%d' % i, sw_path=sw_path, json_path=json_path,
                                thrift_port=thrift_port, pcap_dump=pcap_dump)
            self.aggregation_switch_list.append(sw)
            thrift_port += 1

    def create_edge_switch(self, sw_path, json_path, thrift_port, pcap_dump):
        for i in xrange(self.edge_switch_num):
            sw = self.addSwitch('e%d' % i, sw_path=sw_path, json_path=json_path,
                                thrift_port=thrift_port, pcap_dump=pcap_dump)
            self.edge_switch_list.append(sw)
            thrift_port += 1

    def create_host(self):
        for i in xrange(self.host_num):
            h = self.addHost('h%d' % i)
            self.host_list.append(h)

    def create_link(self):
        for i in xrange(self.edge_switch_num):
            for j in xrange(self.density):
                self.addLink(self.host_list[self.density*i+j], self.edge_switch_list[i])

        step = self.pod_num/2
        for x in xrange(0, self.aggregation_switch_num, step):
            for i in xrange(0, step):
                for j in xrange(0, step):
                    self.addLink(self.aggregation_switch_list[x+i], self.edge_switch_list[x+j])

        for x in xrange(0, self.aggregation_switch_num, step):
            for i in xrange(0, step):
                for j in xrange(0, step):
                    self.addLink(self.core_switch_list[i*step+j], self.aggregation_switch_list[x+i])


def main():
    topology = FatTree(args.behavioral_exe, args.json, args.thrift_port, args.pcap_dump,
                       args.pod_num, args.density)
    net = Mininet(topo=topology,
                  host=P4Host,
                  switch=P4Switch,
                  controller=None)
    net.start()

    sleep(1)

    print "Ready !"

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    main()
