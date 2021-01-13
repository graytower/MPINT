#!/usr/bin/python

import redis
from matplotlib import pyplot as plt
import networkx as nx


def get_node_attr(red_int, node_id):
    int_str = red_int.get(node_id)
    split_str = int_str.split('|')
    length = len(split_str)

    int_dict = {}
    for i in range(length):
        detail_str = split_str[i]
        detail_split_str = detail_str.split(':')
        if len(detail_split_str) != 2:
            continue
        else:
            int_dict[str(detail_split_str[0])] = str(detail_split_str[1])

    return int_dict


# ['7,3,2,1', '11,6,3,2,1', '10,6,3,2,1', '12,9,5,2,1', '8,4,2,1', '13,9,5,2,1']
def get_node(red_int, multi_mc_node_list):
    multi_mc_node_list_len = len(multi_mc_node_list)
    
    node_all = []
    node_id_list = []
    for i in range(multi_mc_node_list_len):
        node_str = multi_mc_node_list[i]
        split_str = node_str.split(',')
        for m in range(0, len(split_str)):
            if split_str[m] in node_id_list:
                continue
            node_attr = get_node_attr(red_int, split_str[m])
            node_tuple = (split_str[m], node_attr)
            node_all.append(node_tuple)
            node_id_list.append(split_str[m])
    
    return node_all


def get_branch_link(multi_mc_node_list):
    multi_mc_node_list_len = len(multi_mc_node_list)
    link_list = []
    
    for i in range(multi_mc_node_list_len):
        node_str = multi_mc_node_list[i]
        split_str = node_str.split(',')
        split_str.reverse()  # change order
        
        for m in range(1, len(split_str)):
            tup = (split_str[m-1], split_str[m])
            if tup in link_list:
                continue
            link_list.append(tup)
            
    return link_list 


def draw_topology(red, red_int):
    tst_dict = red.hgetall("mul")   # dict
    tst_dict_len = len(tst_dict)
    tst_key_list = tst_dict.keys()  # list

    for i in range(tst_dict_len):
        key = tst_key_list[i]
        multi_mc_node_list = list(red.smembers(key))  # transfer set into list
        
        node_all = get_node(red_int, multi_mc_node_list)
        branch_link = get_branch_link(multi_mc_node_list)
        
        g = nx.DiGraph()
        g.clear()
        plt.clf()
        g.add_nodes_from(node_all)
        print g.nodes.data()

        g.add_edges_from(branch_link)
        nx.draw_networkx(g)
        plt.show()
        file_name = "/home/zyan/topo_multi_mc_%s.png" % key
        plt.savefig(file_name)
        red.hdel("mul", key)
        red.delete(key)
		
        check_result = check_topology(g)
        print "check_result: ", check_result
    
    return True   


def read_from_controller(e):
    controller_data = {'1': 1, '2': 3, '3': 2, '4': 1, '5': 1, '6': 2, '7': 1,
                       '8': 1, '9': 2, '10': 1, '11': 1, '12': 1, '13': 1}
    return int(controller_data[e])


def check_topology(topology):
    packet_in = 0
    for e in list(topology.nodes):
        in_degree = topology.in_degree(e)
        if in_degree == 0:
            packet_in += 1

        out_degree = topology.out_degree(e)
        if out_degree == 0:
            continue

        try:
            replicate_count = int(topology.nodes[e]['rep_count'])
        except KeyError:
            replicate_count = read_from_controller(e)

        if int(out_degree) != replicate_count or packet_in > 1:
            return False

    return True


def main():
    red = redis.Redis(unix_socket_path='/var/run/redis/redis.sock', db=1)
    red_int = redis.Redis(unix_socket_path='/var/run/redis/redis.sock', db=4)
    draw_topology(red, red_int)


if __name__ == '__main__':
    main()
