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


# ["0,10,6,3,2,1", "6,11", "3,7", "2,8,4", "2,12,9,5", "9,13"]
def get_node(red_int, single_mc_node_list):
    single_mc_node_list_len = len(single_mc_node_list)
    
    node_all = []
    node_id_list = []
    for i in range(single_mc_node_list_len):
        node_str = single_mc_node_list[i]
        split_str = node_str.split(',')
        for m in range(1, len(split_str)):
            node_attr = get_node_attr(red_int, split_str[m])
            node_tuple = (split_str[m], node_attr)
            node_all.append(node_tuple)
            node_id_list.append(split_str[m])

    return node_all, node_id_list


def get_branch_link(single_mc_node_list, node_id_list):
    single_mc_node_list_len = len(single_mc_node_list)
    link_list = []
    
    for i in range(single_mc_node_list_len):
        node_str = single_mc_node_list[i]
        split_str = node_str.split(',')
        # change order
        ordered_list = []
        ordered_list.append(split_str[0])
        remain_list = split_str[1:]
        remain_list.reverse()
        ordered_list += remain_list
        
        for m in range(1, len(ordered_list)):
            if ordered_list[m-1] == '0' or ordered_list[m-1] not in node_id_list:
                continue
            tup = (ordered_list[m-1], ordered_list[m])
            link_list.append(tup)
            
    return link_list 


def draw_topology(red, red_int):
    tst_dict = red.hgetall("tst")   # dict
    tst_dict_len = len(tst_dict)
    tst_key_list = tst_dict.keys()  # list

    for i in range(tst_dict_len):
        key = tst_key_list[i]
        # single_mc_node_list = ["0,10,6,3,2,1", "6,11", "3,7", "2,8,4", "2,12,9,5", "9,13"]
        single_mc_node_list = list(red.smembers(key))  # transfer set into list

        node_all = get_node(red_int, single_mc_node_list)
        branch_link = get_branch_link(single_mc_node_list, node_all[1])
        
        g = nx.DiGraph()
        g.clear()
        plt.clf()
        g.add_nodes_from(node_all[0])
        g.add_edges_from(branch_link)
        nx.draw_networkx(g)
        plt.show()
        file_name = "/home/zyan/topo_single_mc_%s.png" % key
        plt.savefig(file_name)
        red.hdel("tst", key)
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
    red_int = redis.Redis(unix_socket_path='/var/run/redis/redis.sock', db=3)
    draw_topology(red, red_int)


if __name__ == '__main__':
    main()