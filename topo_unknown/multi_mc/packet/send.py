#!/usr/bin/env python
import sys
import time
import random
from int_hdrs import *

def main():
    identification=random.randint(1,65535)

    pkt = Ether(dst='00:aa:bb:00:00:00', src=get_if_hwaddr('eth0'), type=8224) / \
                IP(id=identification)/PathHeader(int_path_num=0)/IntHeader(int_total_num=0)
                
    try:
        pkt.show2()
        time.sleep(1)
        sendp(pkt, iface='eth0')
        time.sleep(1)
    except KeyboardInterrupt:
        sys.exit()

if __name__ == '__main__':
    main()
