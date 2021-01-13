#!/usr/bin/env python

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.cli import CLI

from p4_mininet import P4Switch, P4Host

import argparse
import os
from time import sleep

parser = argparse.ArgumentParser(description='Mininet demo')
parser.add_argument('--behavioral-exe', help='Path to behavioral executable',
                    type=str, action="store", default="/home/zyan/mininet/behavioral-model/targets/simple_switch/simple_switch")
parser.add_argument('--thrift-port', help='Thrift server port for table updates',
                    type=int, action="store", default=9090)
parser.add_argument('--num-hosts', help='Number of hosts to connect to switch',
                    type=int, action="store", default=7)
parser.add_argument('--json', help='Path to JSON config file',
                    type=str, action="store", required=True)
parser.add_argument('--pcap-dump', help='Dump packets on interfaces to pcap files',
                    type=str, action="store", required=False, default=False)

args = parser.parse_args()


class INTTopo(Topo):
    "Single switch connected to n (< 256) hosts."
    def __init__(self, sw_path, json_path, thrift_port, pcap_dump, n, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)

        self.switch_list = []
        self.host_list = []

        m = 13
        for h in xrange(m):
            switch = self.addSwitch('s%d' % (h + 1),
                                    sw_path = sw_path,
                                    json_path = json_path,
                                    thrift_port = thrift_port,
                                    pcap_dump = pcap_dump)
            self.switch_list.append(switch)
            thrift_port = thrift_port + 1

        for h in xrange(n):
            host = self.addHost('h%d' % (h + 1),
                                ip = "10.0.%d.10/24" % h,
                                mac = '00:04:00:00:00:%02x' %h)
            self.host_list.append(host)
            
        self.addLink(self.host_list[0], self.switch_list[0])
        self.addLink(self.host_list[1], self.switch_list[9])
        self.addLink(self.host_list[2], self.switch_list[10])
        self.addLink(self.host_list[3], self.switch_list[6])
        self.addLink(self.host_list[4], self.switch_list[7])
        self.addLink(self.host_list[5], self.switch_list[11])
        self.addLink(self.host_list[6], self.switch_list[12])
        
        self.addLink(self.switch_list[0], self.switch_list[1])
        self.addLink(self.switch_list[1], self.switch_list[2])
        self.addLink(self.switch_list[1], self.switch_list[3])
        self.addLink(self.switch_list[1], self.switch_list[4])
        self.addLink(self.switch_list[2], self.switch_list[5])
        self.addLink(self.switch_list[2], self.switch_list[6])
        self.addLink(self.switch_list[3], self.switch_list[7])
        self.addLink(self.switch_list[4], self.switch_list[8])
        self.addLink(self.switch_list[5], self.switch_list[9])
        self.addLink(self.switch_list[5], self.switch_list[10])
        self.addLink(self.switch_list[8], self.switch_list[11])
        self.addLink(self.switch_list[8], self.switch_list[12])
        
def main():
    num_hosts = args.num_hosts

    topo = INTTopo(args.behavioral_exe,
                   args.json,
                   args.thrift_port,
                   args.pcap_dump,
                   num_hosts)
    net = Mininet(topo = topo,
                  host = P4Host,
                  switch = P4Switch,
                  controller = None)
    net.start()

    os.system("../flow_table/f.sh")

    for n in xrange(num_hosts):
        h = net.get('h%d' % (n + 1))
        h.describe()
        if n != 0:
            h.cmd("python ../packet/receive.py >/dev/null &")

    sleep(1)

    print "Ready !"

    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    main()
