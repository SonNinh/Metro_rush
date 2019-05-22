#!/usr/bin/env python3
from math import inf


class Station_Line:
    """A station line

    Attributes:
        name (str): The name of the station line
        stations (list): The list of stations on the station line
        circular (bool): Whether the station line is circular
        or not
    """
    def __init__(self, name):
        """Create an empty line with a name

        Args:
            name (str): The name of the station line
        """
        if not isinstance(name, str):
            raise TypeError("name must be a str type object")
        self.name = name
        self.stations = []
        self.circular = False

    def get_stations(self):
        """Get all the stations on the line

        Returns:
            list: The list of stations on the station line
        """
        return self.stations

    def get_station_by_index(self, index):
        """Get a station at a certain index

        Args:
            index (int): the index of the station

        Returns:
            Station: the station at that index

        Raises:
            ValueError: If index is not within the range between 0
                and the amount of stations on the line
        """
        if not isinstance(index, int):
            raise TypeError("index must be an int type object")
        if not (0 <= index <= len(self.stations) - 1):
            raise ValueError("index must be within the range of 0 and\
                             the amount of stations on the line")
        return self.stations[index]

    def get_station_by_name(self, station_name):
        """Get a station with certain name

        Args:
            station_name (str): the name of the station

        Returns:
            Station: a station with that name. None if no station matches the
            criteria
        """
        if not isinstance(station_name, str):
            raise TypeError("station_name must be a str type object")
        for station in self.stations:
            if station.name == station_name:
                return station
        return None

    def add_station(self, station):
        """Add a station into the line.

        Args:
            station (Station): The station that needs to be added
        """
        if isinstance(station, Station):
            if self not in station.connected_lines:
                station.add_crossing_line(self)
            self.stations.append(station)
        else:
            raise TypeError("station must be a Station type object")

    def check_validity(self):
        """Check if the line is valid. It is not valid if there exists
        a duplicate station that is not the last station added to the list

        Returns:
            bool: True if there is no duplicate station or the only duplicate
            is the first and last stations. False otherwise.
        """
        # Loop through each station
        for index, station in enumerate(self.stations[:-1]):
            # Check for duplicate in the rest of the list
            if station in self.stations[index + 1:]:
                # Get the index of the duplicate
                duplicate_index = self.stations.index(
                    station, index + 1
                )
                """
                If the index of the duplicate is not the last index or the
                index of the current station is not 0, return False
                """
                if duplicate_index == len(self.stations) - 1 and not index:
                    self.circular = True
                # Else the line is circular
                else:
                    return False
        return True

    def __str__(self):
        return "%s(\n\t\t%s)" % (
            self.name,
            "\n\t\t".join([str(station) for station in self.stations])
        )


class Station:
    """A station

    Attributes:
        name (str): The name of the station
        trains (list): The list of trains at the station
        connected_lines (list): The list of station lines that go
            through the station
        is_start_end_station (bool): Whether the station is a start or
            end station of the map
        is_intersection (bool): Whether the station has multiple station
            lines go across it or not
    """
    def __init__(self, name):
        """Create a new empty station

        Args:
            name (str): The name of the station
        """
        if not isinstance(name, str):
            raise TypeError("name must be a str type object")
        self.name = name
        self.trains = []
        self.connected_lines = []
        self.is_start_end_station = False
        self.is_intersection = False

    def add_crossing_line(self, new_line):
        """Add a station line that crosses the station

        Args:
            new_line (Station_Line): The new station line that goes
                through the station
        """
        if isinstance(new_line, Station_Line):
            self.connected_lines.append(new_line)
        else:
            raise TypeError("new_line must be a Station_Line type object")

    def __str__(self):
        return self.name

    def __eq__(self, other_station):
        if isinstance(other_station, Station):
            return self.name == other_station.name
        else:
            raise TypeError("other_station must be a Station type object")

    def __hash__(self):
        return hash(self.name)


class Train:
    """A train

    Attributes:
        index (int): the index of the train
        station (Station): the current station that the train is on
        line (Station_Line): the current line that the train is on
    """
    def __init__(self, index, station, starting_line=None):
        """Create a train with an index at a certain station

        Args:
            index (int): The index of the train
            station (Station): The
        """
        if not isinstance(index, int):
            raise TypeError("index must be an int type object")
        elif not isinstance(station, Station):
            raise TypeError("station must be a Station type object")
        self.index = index
        self.station = station
        self.line = starting_line
        self._train_path = None
        self.target = None

    def update_path(self, train_path):
        if not isinstance(train_path, list):
            raise TypeError("train_path must be a list type object")
        elif any([not isinstance(item, Station) for item in train_path]):
            raise ValueError(
                "train_path must contain only Station type objects"
            )
        self._train_path = train_path

    def move(self):
        def move_to_target_station():
            self.station.trains.remove(self)
            self.station = self.target
            self.target.trains.append(self)

        def switch_line():
            self.line = get_shared_line(
                self.target.connected_lines,
                self.station.connected_lines
            )

        if not self._train_path:
            return
        current_station = self.station
        target_station = self.target
        if current_station is target_station or not target_station:
            self.target = self._train_path.pop(0)
            shared_lines = get_shared_line(
                self.target.connected_lines,
                self.line
            )
            if (
                    (
                        self.line is shared_lines or
                        shared_lines and self.line in shared_lines
                    ) and
                    (
                     not self.target.trains or
                     self.target.is_start_end_station
                    )
                 ):
                move_to_target_station()
            else:
                switch_line()
        elif not self.target.trains or self.target.is_start_end_station:
            move_to_target_station()


class Base_Map:
    """Base map

    """
    def __init__(self):
        self.lines = []
        self.trains = []
        self.start_station = None
        self.starting_line = None
        self.end_station = None
        self.possible_paths = None

    def add_line(self, line):
        """
        Add a line into the map

        Input:
            - line: a Station_Line type object
        """
        if isinstance(line, Station_Line):
            self.lines.append(line)
        else:
            raise TypeError("line must be a Station_Line object")

    def get_line(self, line_name):
        """Get a line with certain name

        Input:
            - line_name: a str type object represent the line's name

        Output:
            - a line in the base map with the name given from the input,
            None if there is no line with such name
        """
        if not isinstance(line_name, str):
            raise TypeError("line_name must be a str type object")
        # Search for the line with that name
        for line in self.lines:
            if line.name == line_name:
                return line
        return None

    def get_station_by_line(self, line_name, station_index):
        """Get a station from the map indicates by the name of the line it is on
        and its index

        Input:
            - line_name: a str type object represent the line's name
            - station_index: an int type object represent the index of the
            station on the line

        Output:
            - a station on the line with that index, None if the line doesn't
            exist or index is out of range.
        """
        if not isinstance(line_name, str):
            raise TypeError("line_name must be a str type object")
        if isinstance(station_index, int):
            # Get the line by the name
            desginated_line = self.get_line(line_name)
            if desginated_line:
                # Search on that line for that index
                return desginated_line.get_station_by_index(station_index)
            else:
                return None
        else:
            raise TypeError("station_index must be an int type object")

    def get_station_by_name(self, station_name, line_name=None):
        """
        Get a station from the map indicates by its name.

        Input:
            - station_name: a str type object represent the station's name
            - line_name: a str type object represent the line name. If leaves
            unspecified, will search on all lines.

        Output:
            - a station with that name, None if no station meets the criteria
        """
        if not isinstance(station_name, str):
            raise TypeError("station_name must be a str type object")
        # If line is specified, search for the station on that line
        if isinstance(line_name, str):
            designated_line = self.get_line(line_name)
            return designated_line.get_station_by_name(station_name)
        # Else search all stations
        elif line_name is None:
            for train_line in self.lines:
                result = train_line.get_station_by_name(station_name)
                if result:
                    return result
        else:
            raise TypeError("station_name must be a str type object")
        return None

    def get_stations(self):
        """
        Get the list of all stations in the map
        """
        return_list = []
        # Add all stations on each line to the return list (except duplicate)
        for line in self.lines:
            return_list.extend([
                station for station in line.stations
                if station not in return_list
            ])
        return return_list

    def update_start_end_station(self, line_name, station_index, start=True):
        """Update the starting point and ending point of the map

        Args:
            line_name (str): the name of the line
            station_index (int): the index of the station
            start (bool): whether it's the start station that is getting
                updated or not
        """
        if not isinstance(line_name, str):
            raise TypeError("line_name must be a str type object")
        elif not isinstance(station_index, int):
            raise TypeError("station_index must be an int type object")
        # Get the designated station
        designated_station = self.get_station_by_line(line_name, station_index)
        if not designated_station:
            raise ValueError("Station doesn't exist")
        # Change the end or start station to the designated station
        designated_station.is_start_end_station = True
        if start:
            self.start_station = designated_station
            self.starting_line = self.get_line(line_name)
        else:
            self.end_station = designated_station

    def initialize_trains(self, amount):
        """Create a number of trains on the map

        Input:
            - amount: an int type object represents the amount of
            stations
        """
        if not isinstance(amount, int):
            raise TypeError("amount must be an int type object")
        if not self.start_station:
            raise ValueError("A start station must be designated first")
        for index in range(amount):
            self.trains.append(
                Train(
                    index + 1,
                    self.start_station,
                    self.starting_line
                )
            )

    def distribute_trains(self, path_cost_list):
        """Distribute the amount trains that will go on each path

        Args:
            path_cost_list (list): Contains lists, each has 3 elements
                with the first element is a list of Stations represents
                the raod, the second element is the cost of the cost and
                the third element is whether the path has extra cost
        """
        def get_minimum_cost_path_pair():
            minimum_index = None
            minimum_cost = inf
            for index, pair in enumerate(path_cost_list):
                if pair[1] < minimum_cost:
                    minimum_index = index
                    minimum_cost = pair[1]
            return path_cost_list[minimum_index]

        if not isinstance(path_cost_list, list):
            raise TypeError("paths must be a list type object")
        elif not all(
                isinstance(item, list) and
                len(item) == 3 and
                isinstance(item[0], list) and
                isinstance(item[1], int) and
                isinstance(item[2], bool)
                for item in path_cost_list
                ):
            raise ValueError("Invalid value in path_cost_list")
        try:
            self.possible_paths = [
                item[0] for item in path_cost_list
            ]
            for train in self.trains:
                minimum_pair = get_minimum_cost_path_pair()
                train.update_path(minimum_pair[0][1:])
                minimum_pair[1] += 2 if minimum_pair[2] else 1
        except (ValueError, AttributeError, IndexError):
            return

    def start_run(self):
        def print_station_status():
            """Print all stations that have trains on them
            """
            occupied_station = []
            line_index_list = []
            train_list = []
            for line in self.lines:
                for index, station in enumerate(line.stations):
                    if (station not in occupied_station and
                            station.trains):
                        occupied_station.append(station)
                        line_index_list.append((line.name, index))
                        train_list.append(station.trains)
            print("\n".join([
                "%s(%s:%s)-%s" % (
                    item[0].name,
                    item[1][0],
                    item[1][1] + 1,
                    len(item[2])
                    # ",".join("T%s" % train.index for train in item[2])
                )
                for item in zip(
                    occupied_station, line_index_list, train_list
                )
            ]), end="\n\n")

        if not isinstance(self.start_station, Station):
            raise Exception("Base map does not have a correct start station")
        elif not isinstance(self.end_station, Station):
            raise Exception("Base map does not have a correct end station")
        elif not isinstance(self.starting_line, Station_Line):
            raise Exception("Base map does not have a correct starting line")
        amount_of_trains = len(self.trains)
        turn_counter = 0
        self.start_station.trains = self.trains.copy()
        while len(self.end_station.trains) < amount_of_trains:
            for train in self.trains:
                train.move()
            print("Turn", turn_counter + 1)
            print_station_status()
            turn_counter += 1
        print("Total turn:", turn_counter)

    def __str__(self):
        return "Base_Map(\n    %s\n)\nStart=%s\nEnd=%s" % (
            "\n\t".join([str(line) for line in self.lines]),
            self.start_station,
            self.end_station
        )


def get_shared_line(arg1, arg2):
    def get_shared_line_for_list(list1, list2):
        shared_lines = [line for line in list1 if line in list2]
        return (
            shared_lines[0] if len(shared_lines) == 1 else
            shared_lines if shared_lines else None
        )

    def get_shared_line_for_line(line, line_list):
        return line if line in line_list else None

    if not arg1 or not arg2:
        return None
    elif not isinstance(arg1, (Station_Line, list)):
        raise TypeError("arg1 must be either Station_Line object or a list")
    elif not isinstance(arg2, (Station_Line, list)):
        raise TypeError("arg2 must be either Station_Line object or a list")
    elif (isinstance(arg1, list) and
          any([not isinstance(item, Station_Line) for item in arg1])):
        raise ValueError("arg1 must contain only Station_Line object\
 when it is a list")
    elif (isinstance(arg2, list) and
          any([not isinstance(item, Station_Line) for item in arg2])):
        raise ValueError("arg2 must contain only Station_Line object\
 when it is a list")
    if isinstance(arg1, list) and isinstance(arg2, list):
        return get_shared_line_for_list(arg1, arg2)
    elif isinstance(arg1, Station_Line) and isinstance(arg2, list):
        return get_shared_line_for_line(arg1, arg2)
    elif isinstance(arg1, list) and isinstance(arg2, Station_Line):
        return get_shared_line_for_line(arg2, arg1)
    elif isinstance(arg1, Station_Line) and isinstance(arg2, Station_Line):
        return None if arg1 is not arg2 else arg1
