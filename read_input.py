#!/usr/bin/env python3
from base_graph_and_node import Base_Map, Station, Station_Line, Train
from utility import print_error_message


def process_line_block(index, content, base_map):
    """
    Process a certain block from the content that indicates
    the name of stations that are on the same station line.

    Input:
        - index: an int type object represent the index of the line
        that marks the start of the block in the content
        - content: a list of str type objects
        - base_map: a Base_Map type object represent the whole map

    Output:
        - index: the index at which the block ends
        - new_line: the station line that is converted from the block
    """
    if not isinstance(index, int):
        raise TypeError("index must be an int type object")
    elif not isinstance(content, list):
        raise TypeError("content must be a list type object")
    # Create a new station line
    new_line = Station_Line(content[index][1:].strip())
    # move to next line
    index += 1
    try:
        line_content = content[index].split(":")
        # Loop till the content of the line is no longer a number
        while line_content[0].isdigit():
            # Get station name
            station_name = line_content[1].strip()
            # Search for that station in the base map
            search_station = base_map.get_station_by_name(station_name)
            # Or create new one if the search failed
            new_station = search_station if search_station else Station(
                station_name
            )
            new_line.add_station(new_station)
            index += 1
            line_content = content[index].split(":")
        if not new_line.check_validity():
            print_error_message("Invalid file")
    except ValueError:
        print_error_message("Invalid file")
    return index, new_line


def initialize_amount_of_trains(line_content, base_map):
    """
    Read the line content and initialize trains for the base map

    Input:
        - line_content: a str type object
        - base_map: a Base_Map object
    """
    if not isinstance(line_content, str):
        raise TypeError("line_content must be a str type object")
    elif not isinstance(base_map, Base_Map):
        raise TypeError("base_map must be a Base_Map type object")
    line_content = line_content.split("=", 1)
    try:
        amount_of_trains = int(line_content[1])
    except ValueError:
        print_error_message("Invalid file")
    if amount_of_trains < 0:
        print_error_message("Invalid file")
    base_map.initialize_trains(amount_of_trains)
    

def process_start_end_line(line_content, base_map, end=False):
    if not isinstance(line_content, str):
        raise TypeError("line_content must be a str type object")
    elif not isinstance(base_map, Base_Map):
        raise TypeError("base_map must be a Base_Map type object")
    elif not isinstance(end, bool):
        raise TypeError("end must be a bool type object")
    line_content = line_content.split("=", 1)[1].split(":")
    line_name = line_content[0]
    station_index = line_content[1].strip()
    base_map.update_start_end_station(line_name, int(station_index) - 1, end)
    return line_name, int(station_index) - 1


def read_input(file_name):
    """
    Read the input file and return a train station base map from the data

    Input:
        - file_name: a str type object represents the name of the file

    Output:
        - base_map: a Base_Map type object represents the whole train
        station map
    """
    if not isinstance(file_name, str):
        raise TypeError("file_name must be a str type object")
    with open(file_name, "r") as input_file:
        base_map = Base_Map()
        content = input_file.readlines()
        content_length = len(content)
        index = 0
        while index < content_length:
            line_content = content[index]
            if line_content.startswith("#"):
                index, new_line = process_line_block(index, content, base_map)
                if new_line is None:
                    return
                base_map.add_line(new_line)
            elif line_content.startswith("START="):
                start_node = process_start_end_line(line_content, base_map)
                index += 1
            elif line_content.startswith("END="):
                end_node = process_start_end_line(line_content, base_map, True)
                index += 1
            elif line_content.startswith("TRAINS="):
                initialize_amount_of_trains(line_content, base_map)
                index += 1
            elif line_content.isspace():
                index += 1
            else:
                print_error_message("Invalid file")
        return base_map, start_node, end_node
    return None


def main():
    base_map, start_info, end_info = read_input("map")

    # start_node = base_map.start_station
    # cur_conn_line = start_node.get_conn_lines()
    # print([line.get_stations() for line in cur_conn_line])
    
    # start_node = base_map.get_station_by_line(start_info[0], start_info[1])
    # end_node = base_map.get_station_by_line(end_info[0], end_info[1])

    base_map.get_station_by_line(start_info[0], start_info[1]).over = 1
    layers = [[start_info]]
    bounding_nodes = []
    while end_info not in bounding_nodes:
        bounding_nodes = []
        for node in layers[-1]:
            cur_node = base_map.get_station_by_line(node[0], node[1])

            cur_conn_line = cur_node.get_conn_lines()

            idx = 0
            for i, line in enumerate(cur_conn_line):
                if line.name != node[0]:
                    idx = line.get_stations().index(cur_node)
                    if base_map.get_station_by_line(line.name, idx).over < len(cur_conn_line):
                        bounding_nodes.append((line.name, idx))
                        base_map.get_station_by_line(line.name, idx).over += 1
                        
                else:
                    if node[1] > 0 and base_map.get_station_by_line(node[0], node[1]-1).over == 0:
                        bounding_nodes.append((node[0], node[1]-1))
                        base_map.get_station_by_line(node[0], node[1]-1).over += 1
                    if node[1] < len(line.get_stations())-1 and base_map.get_station_by_line(node[0], node[1]+1).over == 0:
                        bounding_nodes.append((node[0], node[1]+1))
                        base_map.get_station_by_line(node[0], node[1]+1).over += 1
                
                    

        if not  bounding_nodes:
            break

        layers.append(bounding_nodes)


    path = [end_info]
    cur_info = end_info
    for layer in reversed(layers[:-1]):
        for node in layer:
            if node[0] == cur_info[0]:
                if abs(node[1]-cur_info[1]) == 1:
                    cur_info = node
                    path.insert(0, cur_info)
                    break
            elif base_map.get_station_by_line(node[0], node[1]) == base_map.get_station_by_line(cur_info[0], cur_info[1]):
                cur_info = node
                path.insert(0, cur_info)
                break

    for i in path:
        print(base_map.get_station_by_line(i[0], i[1]).name)


def bfs(base_map, train, end_info, th):

    base_map.get_station_by_line(train.line, train.index).over = 1
    layers = [[[train.line, train.index]]]
    bounding_nodes = []
    while end_info not in bounding_nodes:
        bounding_nodes = []
        for node in layers[-1]:
            cur_node = base_map.get_station_by_line(node[0], node[1])

            cur_conn_line = cur_node.get_conn_lines()

            idx = 0
            for i, line in enumerate(cur_conn_line):
                if line.name != node[0]:
                    idx = line.get_stations().index(cur_node)
                    if base_map.get_station_by_line(line.name, idx).over < len(cur_conn_line):
                        bounding_nodes.append((line.name, idx))
                        base_map.get_station_by_line(line.name, idx).over += 1
                        
                else:
                    if node[1] > 0 and base_map.get_station_by_line(node[0], node[1]-1).over == 0:
                        bounding_nodes.append((node[0], node[1]-1))
                        base_map.get_station_by_line(node[0], node[1]-1).over += 1
                    if node[1] < len(line.get_stations())-1 and base_map.get_station_by_line(node[0], node[1]+1).over == 0:
                        bounding_nodes.append((node[0], node[1]+1))
                        base_map.get_station_by_line(node[0], node[1]+1).over += 1

        if not  bounding_nodes:
            return None

        layers.append(bounding_nodes)

    path = []
    cur_info = end_info
    for layer in reversed(layers):
        for node in layer:
            base_map.get_station_by_line(node[0], node[1]).over = 0
            if node[0] == cur_info[0]:
                if abs(node[1]-cur_info[1]) == 1:
                    cur_info = node
                    path.insert(0, cur_info)
                    
            elif base_map.get_station_by_line(node[0], node[1]) == base_map.get_station_by_line(cur_info[0], cur_info[1]):
                cur_info = node
                path.insert(0, cur_info)
                

    # for i in path:
    #     print(base_map.get_station_by_line(i[0], i[1]).name)
    try:

        return path[1]
    except Exception:
        return end_info


def main2():
    base_map, start_info, end_info = read_input("delhi-metro-stations")
    base_map.get_station_by_line(start_info[0], start_info[1]).occupied = True
    ls_trains = []
    num_train = 0
    compl = []
    while len(compl)<30:
        print(num_train)
        if len(ls_trains)<60:
            train1 = Train(start_info[0], start_info[1])
            ls_trains.append(train1)
            train2 = Train(start_info[0], start_info[1])
            ls_trains.append(train2)
        base_map.get_station_by_line(start_info[0], start_info[1]).occupied = True

        for th, train in enumerate(ls_trains):
            print(ls_trains[0].done)
            if not train.done:
                train.path.append((train.line, train.index))
                bounding_nodes = []
                cur_node = base_map.get_station_by_line(train.line, train.index)
                cur_conn_line = cur_node.get_conn_lines()

                for i, line in enumerate(cur_conn_line):
                    if line.name != train.line:
                        idx = line.get_stations().index(cur_node)
                        # if not base_map.get_station_by_line(line.name, idx).occupied:
                        bounding_nodes.append((line.name, idx))
                            # base_map.get_station_by_line(line.name, idx).over = True
                            
                    else:
                        if train.index > 0 and not base_map.get_station_by_line(train.line, train.index-1).occupied:
                            bounding_nodes.append((train.line, train.index-1))
                            # base_map.get_station_by_line(node[0], node[1]-1).occupied = True
                        if train.index < len(line.get_stations())-1 and not base_map.get_station_by_line(train.line, train.index+1).occupied:
                            bounding_nodes.append((train.line, train.index+1))
                            # base_map.get_station_by_line(node[0], node[1]+1).occupied = True
                # print(bounding_nodes)
                if len(bounding_nodes) == 1:
                    print('a')
                    new_node = base_map.get_station_by_line(bounding_nodes[0][0], bounding_nodes[0][1])
                    
                    if bounding_nodes[0][0] == end_info[0] and bounding_nodes[0][1] == end_info[1]:
                        print("ninh son")
                        num_train += 1
                        compl.append(th)
                        train.done = True
                        train.line = bounding_nodes[0][0]
                        train.index = bounding_nodes[0][1]
                        cur_node.occupied = False
                    else:
                        if not new_node.occupied:
                            new_node.occupied = True
                        
                            cur_node.occupied = False
                            train.line = bounding_nodes[0][0]
                            train.index = bounding_nodes[0][1]
                        elif new_node == cur_node:
                            train.line = bounding_nodes[0][0]
                            train.index = bounding_nodes[0][1]
                elif len(bounding_nodes) > 1:
                    print('b')
                    next_node = bfs(base_map, train, end_info, th)
                    if next_node:
                        new_node = base_map.get_station_by_line(next_node[0], next_node[1])
                        if next_node[0] == end_info[0] and next_node[1] == end_info[1]:
                            print("skgjbsdflkgdsbfgkjsdngkdjfb")
                            num_train += 1
                            compl.append(th)
                            train.done = True
                            train.line = next_node[0]
                            train.index = next_node[1]
                            cur_node.occupied = False
                        else:
                            if not new_node.occupied:
                                new_node.occupied = True
                                cur_node.occupied = False
                                train.line = next_node[0]
                                train.index = next_node[1]
                            elif new_node == cur_node:
                                train.line = next_node[0]
                                train.index = next_node[1]
    
                    

        for i, train in enumerate(ls_trains):
            print(i, train.line, train.index)
        print()


    print(compl)
    for i in compl:
        path = ls_trains[i].path
        print("cost:", len(path)+1)
        for stat in path:
            print(stat)
            # print(base_map.get_station_by_line(stat[0], stat[1]))

        print()


if __name__ == "__main__":
    main2()
    