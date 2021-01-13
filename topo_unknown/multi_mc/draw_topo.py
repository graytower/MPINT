#!/usr/bin/python

import redis
from matplotlib import pyplot as plt
import networkx as nx


def getNodeAttr(red_int, node_id):
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
def getNode(red_int, multi_mc_node_list):
    multi_mc_node_list_len = len(multi_mc_node_list)
    
    node_list = []
    for i in range(multi_mc_node_list_len):
        str = multi_mc_node_list[i]
        strSplit = str.split(',')
        for m in range(0,len(strSplit)):
            if strSplit[m] in node_list:
                continue
            node_attr = getNodeAttr(red_int, strSplit[m])
            node_tuple = (strSplit[m], node_attr)            
            node_list.append(node_tuple)
    
    return node_list                


def getBranceLink(multi_mc_node_list):
    multi_mc_node_list_len = len(multi_mc_node_list)
    link_list = []
    
    for i in range(multi_mc_node_list_len):
        str = multi_mc_node_list[i]
        strSplit = str.split(',')
        strSplit.reverse()        #change order
        
        for m in range(1,len(strSplit)):
            tup = (strSplit[m-1], strSplit[m])
            if tup in link_list:
                continue
            link_list.append(tup)
            
    return link_list 


def draw_topo(red, red_int):
    tst_dict = red.hgetall("mul")#dict
    tst_dict_len = len(tst_dict)
    tst_key_list = tst_dict.keys()#list

    for i in range(tst_dict_len):
        key = tst_key_list[i]
        multi_mc_node_list = []
        multi_mc_node_list = list(red.smembers(key))#transfer set into list
        
        node_all = getNode(red_int, multi_mc_node_list)
        branch_link = getBranceLink(multi_mc_node_list)
        
        G=nx.Graph()
        G.clear()
        plt.clf()
        G.add_nodes_from(node_all)
        print G.nodes.data()

        G.add_edges_from(branch_link)
        nx.draw_networkx(G)
        plt.show()
        file_name = "/home/zyan/topo_multi_mc_%s.png" % (key)
        plt.savefig(file_name)
        red.hdel("mul", key)
        red.delete(key)
    
    return True   


def main():
    red = redis.Redis(unix_socket_path='/var/run/redis/redis.sock',db=1)
    red_int = redis.Redis(unix_socket_path='/var/run/redis/redis.sock',db=4)
    draw_topo(red, red_int)


if __name__ == '__main__':
    main()
