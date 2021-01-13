import redis


def parse_int_info(int_str):
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


def main():
    red = redis.Redis(unix_socket_path='/var/run/redis/redis.sock', db=2)
    int_dict = red.hgetall('topo')
    int_dict_len = len(int_dict)
    int_key_list = int_dict.keys()

    for i in range(int_dict_len):
        sw_id = int_key_list[i]
        int_str = red.get(sw_id)        
        node_attr = parse_int_info(int_str)
        print node_attr


if __name__ == '__main__':
    main()
