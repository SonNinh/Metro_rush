#!/usr/bin/env python3
from base_graph import Base_Map, Station, Station_Line, Train
from utility import print_error_message
from time import time
from math import sin, cos, atan2, pi
import csv


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
    except (ValueError):
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
    # base_map.initialize_trains(amount_of_trains)
    return amount_of_trains


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
                amount_of_trains = initialize_amount_of_trains(line_content, base_map)
                index += 1
            elif line_content.isspace():
                index += 1
            else:
                print_error_message("Invalid file")
        return base_map, start_node, end_node, amount_of_trains
    return None


def minimize(path):
    result = [path[0]]
    for node in path:
        if node != result[-1]:
            result.append(node)
    return result


def find_path(layers, base_map, end_info):
    path = []
    cur_info = end_info

    for layer in reversed(layers):
        print(layer)

        for node in layer:
            base_map.get_station_by_line(node[0], node[1]).over = 0
            # print(len(base_map.get_line(node[0]).get_stations()), abs(node[1] - cur_info[1]))
            if node[0] == cur_info[0]:
                if abs(node[1]-cur_info[1]) == 1:
                    cur_info = node
                    path.insert(0, cur_info)

                elif abs(node[1] - cur_info[1]) == len(base_map.get_line(node[0]).get_stations())-2:
                    cur_info = node
                    path.insert(0, cur_info)

            elif base_map.get_station_by_line(node[0], node[1]) == base_map.get_station_by_line(cur_info[0], cur_info[1]):
                cur_info = node
                path.insert(0, cur_info)
    print(path)
    return path


def find_bounding_nodes(base_map, layers, start_info):
    bounding_nodes = []
    for node in layers[-1]:
        cur_node = base_map.get_station_by_line(node[0], node[1])
        cur_conn_line = cur_node.get_conn_lines()

        idx = 0
        for i, line in enumerate(cur_conn_line):
            all_stations = line.get_stations()
            if line.name != node[0]:
                idx = line.get_stations().index(cur_node)
                if all_stations[idx].over < 2:
                    if not (line.name == start_info[0] and idx == start_info[1]):
                        bounding_nodes.append((line.name, idx))
                        all_stations[idx].over += 1
            else:
                if node[1] > 0 and all_stations[node[1]-1].over == 0:
                    if not (node[0] == start_info[0] and node[1]-1 == start_info[1]):
                        bounding_nodes.append((node[0], node[1]-1))
                        all_stations[node[1]-1].over += 1
                elif node[1] == 0:
                    if all_stations[0] == all_stations[-1] and all_stations[-2].over == 0:
                        # bounding_nodes.append((node[0], len(line.get_stations())-1))
                        bounding_nodes.append((node[0], len(all_stations)-2))
                        all_stations[-2].over += 1

                if node[1] < len(line.get_stations())-1 and all_stations[node[1]+1].over == 0:
                    if not (node[0] == start_info[0] and node[1]+1 == start_info[1]):
                        bounding_nodes.append((node[0], node[1]+1))
                        all_stations[node[1]+1].over += 1
                elif node[1] == len(all_stations)-1:
                    if all_stations[0] == all_stations[-1] and all_stations[1].over == 0:
                        # bounding_nodes.append((node[0], 0))
                        bounding_nodes.append((node[0], 1))
                        all_stations[1].over += 1

    return bounding_nodes


def bfs(base_map, train, start_info, end_info, th):
    '''
    find sortest path from specified train to ending station using BFS
    '''
    base_map.get_station_by_line(train.line, train.index).over = 1
    layers = [[[train.line, train.index]]]
    bounding_nodes = []
    while end_info not in bounding_nodes:
        bounding_nodes = find_bounding_nodes(base_map, layers, start_info)
        if not bounding_nodes:
            return None
        layers.append(bounding_nodes)

    path = find_path(layers, base_map, end_info)

    try:
        return path[1]
    except Exception:
        return end_info


def main():
    # base_map, start_info, end_info, amount_of_trains = read_input("circular_test")
    base_map, start_info, end_info, amount_of_trains = read_input("delhi-metro-stations")
    base_map.get_station_by_line(start_info[0], start_info[1]).occupied = True
    ls_trains = []
    num_train = 0
    compl = []
    while len(compl) < amount_of_trains:
        # print('complete', len(compl), 'num train:', len(ls_trains))
        if len(ls_trains) < amount_of_trains*5:
            train1 = Train(start_info[0], start_info[1])
            ls_trains.append(train1)
            train2 = Train(start_info[0], start_info[1])
            ls_trains.append(train2)

        base_map.get_station_by_line(start_info[0], start_info[1]).occupied = True

        for th, train in enumerate(ls_trains):
            if not train.done:
                train.path.append((train.line, train.index))
                bounding_nodes = []
                cur_node = base_map.get_station_by_line(train.line, train.index)
                cur_conn_line = cur_node.get_conn_lines()

                for i, line in enumerate(cur_conn_line):
                    all_stations = line.get_stations()
                    if line.name != train.line:
                        idx = all_stations.index(cur_node)
                        bounding_nodes.append((line.name, idx))
                    else:
                        if train.index > 0 and not all_stations[train.index-1].occupied:
                            bounding_nodes.append((train.line, train.index-1))
                        else:
                            if all_stations[0] == all_stations[-1] and not all_stations[-2].occupied:
                                bounding_nodes.append((train.line, len(all_stations)-2))

                        if train.index < len(line.get_stations())-1 and not all_stations[train.index+1].occupied:
                            bounding_nodes.append((train.line, train.index+1))
                        else:
                            if all_stations[0] == all_stations[-1] and not all_stations[1].occupied:
                                bounding_nodes.append((train.line, 1))

                if len(bounding_nodes) == 1:
                    # if there is only 1 possible station to move from current train
                    new_node = base_map.get_station_by_line(bounding_nodes[0][0], bounding_nodes[0][1])

                    if bounding_nodes[0] == end_info:
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
                            # at interchange
                            train.line = bounding_nodes[0][0]
                            train.index = bounding_nodes[0][1]
                elif len(bounding_nodes) > 1:
                    # if there are more than 1 possible stations to move from current train
                    next_node = bfs(base_map, train, start_info, end_info, th)
                    if next_node:
                        new_node = base_map.get_station_by_line(next_node[0], next_node[1])
                        if next_node == end_info:
                            # if next staion is the end staion
                            num_train += 1
                            compl.append(th)
                            train.done = True
                            cur_node.occupied = False
                        else:
                            if not new_node.occupied:
                                new_node.occupied = True
                                cur_node.occupied = False

                        train.line = next_node[0]
                        train.index = next_node[1]

        # for i, train in enumerate(ls_trains):
        #     print(i, train.line, train.index)
        # print()
    compl.sort()
    print(compl)

    for i in compl:
        ls_trains[i].done = False
        ls_trains[i].path = minimize(ls_trains[i].path)
        ls_trains[i].path.append(end_info)
        print(ls_trains[i].path)
        print()

    ls_stations = base_map.get_stations()
    num_train = 0
    cost = 0
    start_node = base_map.get_station_by_line(start_info[0], start_info[1])
    end_node = base_map.get_station_by_line(end_info[0], end_info[1])
    for i in compl:
        start_node.trains.append((i, start_info[0], start_info[1]))
    while num_train < amount_of_trains:
        cost += 1
        for i in compl:
            if not ls_trains[i].done:
                # print(len(ls_trains[i].path), i)
                if len(ls_trains[i].path) > 1:
                    station_info = ls_trains[i].path[1]
                    station = base_map.get_station_by_line(station_info[0], station_info[1])
                    if (not station.trains) or station == end_node or station.trains[0][0] == i:
                        pre_station_info = ls_trains[i].path[0]
                        pre_station = base_map.get_station_by_line(pre_station_info[0], pre_station_info[1])
                        if pre_station_info == start_info:
                            try:
                                pop_idx = pre_station.trains.index((i, start_info[0], start_info[1]))
                                pre_station.trains.pop(pop_idx)
                            except Exception:
                                pass

                        else:
                            pre_station.trains = []
                        if station_info == end_info:
                            station.trains.append((i, station_info[0], station_info[1]))
                        else:
                            station.trains = [(i, station_info[0], station_info[1])]
                        ls_trains[i].path.pop(0)
                else:
                    ls_trains[i].done = True
                    num_train += 1

        string = ''
        for sta in ls_stations:
            if sta.trains:
                string += sta.name+'('+sta.trains[0][1]+':'+str(sta.trains[0][2]+1)+')'+'-'
                for tau in sta.trains:
                    string += 'T'+str(tau[0])
                string += '|'
        print(string)
        print(len(base_map.get_station_by_line(end_info[0], end_info[1]).trains))
        print()
    print('cost:', cost)
    # for i in compl:
    #     print(ls_trains[i].path)'''


def draw_tail():
    pass


def draw_line(line_for_draw, ls_sta_located, ls_lines_not_drawed, base_map, angle):
    delta = 10
    ls_stations = line_for_draw.get_stations()
    for sta in ls_stations:

        if sta.located:
            print('as')
            ref_station = sta
            idx_a = ls_stations.index(ref_station)
            idx_b = ls_stations.index(ref_station)
            break
    else:
        idx_a = 0
        idx_b = 0
    ref_angle = angle

    print('index:', idx_a, idx_b)
    while idx_a < len(ls_stations)-1:
        # print('as')
        for th, station in enumerate(ls_stations[idx_a+1:], idx_a+1):
            conn_lines = station.get_conn_lines()
            if len(conn_lines) > 1:
                for line in conn_lines:
                    if line.name not in ls_lines_not_drawed and not line.drawed:
                        ls_lines_not_drawed.append(line.name)

                if station.located:
                    diff_x = ls_stations[th].pos[0]-ls_stations[idx_a].pos[0]
                    diff_y = ls_stations[th].pos[1]-ls_stations[idx_a].pos[1]
                    for i, station in enumerate(ls_stations[idx_a+1:th], 1):
                        station.pos[0] = int(ls_stations[idx_a].pos[0] + diff_x//(abs(th-idx_a))*i)
                        station.pos[1] = int(ls_stations[idx_a].pos[1] + diff_y//(abs(th-idx_a))*i)
                        station.located = True
                    idx_a = th
                    ref_angle = atan2(diff_y, diff_x)
                    break
        else:
            # draw_tail()
            for th, station in enumerate(ls_stations[idx_a+1:], idx_a+1):
                station.pos[0] = int(delta*cos(ref_angle)) + ls_stations[th-1].pos[0]
                station.pos[1] = int(delta*sin(ref_angle)) + ls_stations[th-1].pos[1]
                station.located = True
            idx_a = len(ls_stations)-1

    th = idx_b
    while idx_b > 0:
        # print('as')

        for station in reversed(ls_stations[:idx_b]):
            th -= 1
            conn_lines = station.get_conn_lines()
            if len(conn_lines) > 1:
                for line in conn_lines:
                    if line.name not in ls_lines_not_drawed and not line.drawed:
                        ls_lines_not_drawed.append(line.name)

                if station.located:
                    diff_x = ls_stations[th].pos[0]-ls_stations[idx_b].pos[0]
                    diff_y = ls_stations[th].pos[1]-ls_stations[idx_b].pos[1]
                    i = 0
                    for station in reversed(ls_stations[th:idx_b]):
                        i += 1
                        station.pos[0] = int(ls_stations[idx_b].pos[0] + diff_x//(abs(th-idx_b))*i)
                        station.pos[1] = int(ls_stations[idx_b].pos[1] + diff_y//(abs(th-idx_b))*i)
                        station.located = True
                    idx_b = th
                    ref_angle = atan2(diff_y, diff_x)
                    break
        else:
            # draw_tail()
            th = idx_b
            for station in reversed(ls_stations[:idx_b]):
                th -= 1
                station.pos[0] = -int(delta*cos(ref_angle)) + ls_stations[th+1].pos[0]
                station.pos[1] = -int(delta*sin(ref_angle)) + ls_stations[th+1].pos[1]
                station.located = True
            idx_b = 0

    # for line_name in ls_lines_not_drawed:
    #     line_draw = base_map.get_line(line_name)
    #     if not line_draw.drawed:
    #         draw_line(line_draw, ls_sta_located, ls_lines_not_drawed, base_map, 0)


def main_gui():
    base_map, start_info, end_info, amount_of_trains = read_input("delhi-metro-stations")

    all_lines = base_map.get_all_lines()
    # for line in lines:
    #     print(line.name)
    ls_sta_located = []
    ls_lines_not_drawed = []

    with open('stations.csv', 'w', newline='') as f:
        thewriter = csv.writer(f)

        ls_lines = base_map.get_all_lines()
        for th, line in enumerate(ls_lines):
            # line_for_draw = base_map.get_line('Red Line')
            if not line.drawed:
                print(line.name)
                draw_line(line, ls_sta_located, ls_lines_not_drawed, base_map, th*pi/2)

            header = '#'+line.name
            thewriter.writerow([header])
            for station in line.get_stations():
                print(station.pos, station.located)
                thewriter.writerow([station.name, station.pos[0], station.pos[1]])

        # line_for_draw = base_map.get_line('Pink Line')
        # if not line_for_draw.drawed:
        #     draw_line(line_for_draw, ls_sta_located, ls_lines_not_drawed, base_map, 0)
        #
        # header = '#'+line_for_draw.name
        # thewriter.writerow([header])
        # for station in line_for_draw.get_stations():
        #     print(station.pos, station.located)
        #     thewriter.writerow([station.name, station.pos[0], station.pos[1]])
        #
        # line_for_draw = base_map.get_line('Yellow Line')
        # if not line_for_draw.drawed:
        #     draw_line(line_for_draw, ls_sta_located, ls_lines_not_drawed, base_map, pi/2)
        #
        # header = '#'+line_for_draw.name
        # thewriter.writerow([header])
        # for station in line_for_draw.get_stations():
        #     print(station.pos, station.located)
        #     thewriter.writerow([station.name, station.pos[0], station.pos[1]])
        #
        # line_for_draw = base_map.get_line('Blue Line')
        # if not line_for_draw.drawed:
        #     draw_line(line_for_draw, ls_sta_located, ls_lines_not_drawed, base_map, 0)
        #
        # header = '#'+line_for_draw.name
        # thewriter.writerow([header])
        # for station in line_for_draw.get_stations():
        #     print(station.pos, station.located)
        #     thewriter.writerow([station.name, station.pos[0], station.pos[1]])
        #
        # line_for_draw = base_map.get_line('Red Line')
        # if not line_for_draw.drawed:
        #     draw_line(line_for_draw, ls_sta_located, ls_lines_not_drawed, base_map, pi/5)
        #
        # header = '#'+line_for_draw.name
        # thewriter.writerow([header])
        # for station in line_for_draw.get_stations():
        #     print(station.pos, station.located)
        #     thewriter.writerow([station.name, station.pos[0], station.pos[1]])
        #
        # line_for_draw = base_map.get_line('Magenta Line')
        # if not line_for_draw.drawed:
        #     draw_line(line_for_draw, ls_sta_located, ls_lines_not_drawed, base_map, pi/6)
        #
        # header = '#'+line_for_draw.name
        # thewriter.writerow([header])
        # for station in line_for_draw.get_stations():
        #     print(station.pos, station.located)
        #     thewriter.writerow([station.name, station.pos[0], station.pos[1]])
        #
        # line_for_draw = base_map.get_line('Violet Line')
        # if not line_for_draw.drawed:
        #     draw_line(line_for_draw, ls_sta_located, ls_lines_not_drawed, base_map, pi/7)
        #
        # header = '#'+line_for_draw.name
        # thewriter.writerow([header])
        # for station in line_for_draw.get_stations():
        #     print(station.pos, station.located)
        #     thewriter.writerow([station.name, station.pos[0], station.pos[1]])


if __name__ == "__main__":
    # main()
    main_gui()
