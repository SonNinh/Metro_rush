#!/usr/bin/env python3
class Station_Line:
    def __init__(self, name):
        if not isinstance(name, str):
            raise TypeError("name must be a str type object")
        self.name = name
        self.stations = []
        self.crossing_lines = {}
        self.circular = False
    
    def get_stations(self):
        return self.stations

    def get_station_by_index(self, index):
        """
        Get a station at a certain index

        Input:
            - index: an int type object represents the index of the
            station
        
        Output:
            - the station at that index
        """
        if not isinstance(index, int):
            raise TypeError("index must be an int type object")
        if not (0 <= index <= len(self.stations) - 1):
            raise ValueError("index must be within the range from 0 and",
                             "the amount of stations in the line")
        return self.stations[index]
    
    def get_station_by_name(self, station_name):
        """
        Get a station with certain name

        Input:
            - station_name: a str type object represents the name of the
            station

        Output:
            - a station with that name or None if no station matches the
            criteria
        """
        if not isinstance(station_name, str):
            raise TypeError("station_name must be a str type object")
        for station in self.stations:
            if station.name == station_name:
                return station
        return None

    def add_station(self, station):
        """
        Add a station into the line.

        Input:
            - station: a Station type object
        """
        if isinstance(station, Station):
            station.update_line(self)
            self.stations.append(station)
        else:   
            raise TypeError("station must be a Station type object")

    def add_crossing_line(self, line_name, connect_station):
        """
        Add a crosssing line to the crossing line dictionary,
        with the key is that line name and the value is the list
        of stations that the two lines share with each other.

        Input:
            - line_name: a str type object represents the name of the crossing
            line
            - connect_station: a Station type object represents the interchange
        """
        if not isinstance(line_name, str):
            raise TypeError("line_name must be a Station_Line type object")
        elif not isinstance(connect_station, Station):
            raise TypeError("connect_station must be a Station type object")
        if connect_station not in self.stations:
            raise ValueError("the given station does not belong to this line")
        try:
            self.crossing_lines[line_name].append(connect_station)
        except KeyError:
            self.crossing_lines[line_name] = [connect_station]

    def check_validity(self):
        """
        Check if the line is valid. It is not valid if there exists
        a duplicate station that is not the last station added to the list

        Output:
            - True if there is no duplicate station or the only duplicate
            is the first and last stations. False otherwise.
        """
        # Loop through each station
        for index, station in enumerate(self.stations[:-2]):
            # Check for duplicate in the rest of the list
            if station in self.stations[index + 1:]:
                # Get the index of the duplicate
                duplicate_index = self.stations[index + 1:].index(
                    station
                )
                """
                If the index of the duplicate is not the last index or the
                index of the current station is not 0, return False
                """
                if duplicate_index != len(self.stations) - 1 or not index:
                    return False
                # Else the line is circular
                else:
                    self.circular = True
        return True

    def __str__(self):
        return "%s(\n\t\t%s)" % (
            self.name, 
            "\n\t\t".join([str(station) for station in self.stations])
        )


class Station:
    def __init__(self, name):
        if not isinstance(name, str):
            raise TypeError("name must be a str type object")
        self.name = name
        self.trains = []
        self.connected_lines = []
        self.over = 0
        self.occupied = False
    
    def update_line(self, new_line):
        """
        Update a line that the station connect with

        Input:
            - new_line: a Station_Line type object
        """
        if isinstance(new_line, Station_Line):
            for line in self.connected_lines:
                line.add_crossing_line(new_line.name, self)
            self.connected_lines.append(new_line)
        else:
            raise TypeError("new_line must be a Station_Line type object")

    def get_conn_lines(self):
        return self.connected_lines


    def __str__(self):
        return self.name
    
    def __eq__(self, other_station):
        if isinstance(other_station, Station):
            return self.name == other_station.name
        else:
            raise TypeError("other_station must be a Station type object")


class Train:
    def __init__(self, line, index):
        self.index = index
        self.line = line
        self.done = False
        self.path = []


class Base_Map:
    def __init__(self):
        self.lines = []
        self.trains = []
        self.start_station = None
        self.end_station = None
    
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
        """
        Get a certain line

        Input:
            - line_name: a str type object represent the line's name

        Output:
            - a line in the base map with the name given from the input,
            None if there is no line with such name
        """
        if not isinstance(line_name, str):
            raise TypeError("line_name must be a str type object")
        for line in self.lines:
            if line.name == line_name:
                return line
        return None

    def get_station_by_line(self, line_name, station_index):
        """
        Get a station from the map indicates by the name of the line it is on
        and its index

        Input:
            - line_name: a str type object represent the line's name
            - station_index: an int type object represent the index of the
            station on the line

        Output:
            - a station on the line with that index, None if the line doesn't exist
            or index is out of range.
        """
        if not isinstance(line_name, str):
            raise TypeError("line_name must be a str type object")
        if isinstance(station_index, int):
            try:
                # Get the line by the name
                desginated_line = self.get_line(line_name)
                # Search on that line for that index
                return desginated_line.get_station_by_index(station_index)
            except AttributeError:
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
            for line in self.lines:
                result = line.get_station_by_name(station_name)
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
        # Get all the stations on each line and merge them together
        for line in self.lines:
            return_list.extend(line.get_stations())
        # Remove duplicate
        return list(set(return_list))

    def update_start_end_station(self, line_name, station_index, end=False):
        """
        Update the starting point and ending point of the map

        Input:
            - line_name: a str type object represents the name of the line
            - station_index: an int type object represents the index of the
            station
            - end: a bool type object represents whether it's the end station
            that is getting updated or not
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
        if end:
            self.end_station = self.get_station_by_line(
                line_name, station_index
            )
        else:
            self.start_station = self.get_station_by_line(
                line_name, station_index
            )
    
    def initialize_trains(self, amount):
        """
        Create a number of trains on the map

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
                    self.start_station
                )
            )

    def __str__(self):
        return "Base_Map(\n    %s\n)\nStart=%s\nEnd=%s" % (
            "\n\t".join([str(line) for line in self.lines]),
            self.start_station,
            self.end_station
        )
