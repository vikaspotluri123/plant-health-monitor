'''
routing.py takes in 4 gps coordinates in a rectangular configuration
It then creates a list of coordinates to travel to and take pictures at
'''

import sys
from numpy import arange

# configuration for distance between pictures in meters
GRID_UNIT = 10

# configuration for overage margin on edge of path
MARGIN = 200

# hard code meter conversions for College Station TX
METERS_IN_DEG_LAT = 111320
METERS_IN_DEG_LON = 95944

# get grid unit steps in terms of lat and lon
LON_AXIS_STEP = GRID_UNIT / METERS_IN_DEG_LAT
LAT_AXIS_STEP = GRID_UNIT / METERS_IN_DEG_LON

# get overlap margins in terms of lat and lon
# LONG_MARGIN = MARGIN / METERS_IN_DEG_LAT
# LAT_MARGIN = MARGIN / METERS_IN_DEG_LON

# make class to store coordinates
class Coordinate:
    '''
    Stores gps coordinates
    '''
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    # this allows coordinates to be printed
    def __str__(self):
        return str(self.latitude) + ', ' + str(self.longitude)

# check if validation passes
def validate_distance(h_distance, v_distance):
    '''
    checks that we are getting the expected distance between each generated coordinate
    '''
    total_distance = (h_distance**2 + v_distance**2)**(0.5)
    difference = abs(total_distance - GRID_UNIT)
    tolerance = GRID_UNIT*0.5

    # print(total_distance, difference, tolerance, difference < tolerance)
    return difference < tolerance

class Navigation:
    '''
    Contains functions necessary for creating the route
    '''
    def create_path(self, c_1, c_2, c_3):
        # calculate side1 latitude, longitude, and distance in meters
        side1lat = (c_2.latitude - c_1.latitude) * METERS_IN_DEG_LAT
        side1lon = (c_2.longitude - c_1.longitude) * METERS_IN_DEG_LON
        side1dist = (side1lat**2 + side1lon**2)**(0.5)

        # calculate side2 latitude, longitude, and distance in meters
        side2lat = (c_3.latitude - c_2.latitude) * METERS_IN_DEG_LAT
        side2lon = (c_3.longitude - c_2.longitude) * METERS_IN_DEG_LON
        side2dist = (side2lat**2 + side2lon**2)**(0.5)

        path = []

        # get number of points on bots sides
        nums1 = len(arange(0, side1dist, GRID_UNIT))
        nums2 = len(arange(0, side2dist, GRID_UNIT))

        # get distance between each point in latitude and longitude
        hsteps1 = side1lat / nums1
        vsteps1 = side1lon / nums1
        hsteps2 = side2lat / nums2
        vsteps2 = side2lon / nums2
        
        # start point half of a step away from each side
        mover = Coordinate(c_1.latitude * METERS_IN_DEG_LAT + hsteps1/2 + hsteps2/2, c_1.longitude * METERS_IN_DEG_LON + vsteps1/2 + vsteps2/2)
        
        # this boolean makes the snake pattern of the path
        reverse = False

        for _out in range(0,nums2):
            tempPath = []

            for _in in range(0,nums1):
                # add points to inner path for a single line
                tempPath.append(Coordinate(mover.latitude / METERS_IN_DEG_LAT, mover.longitude / METERS_IN_DEG_LON))

                if not validate_distance(hsteps1, vsteps1):
                    sys.exit("ERROR: Distance between coordinates is not within 50%% of expected value")

                # fix order if we are on a reverse row
                if reverse:
                    mover.latitude -= hsteps1
                    mover.longitude -= vsteps1
                else:
                    mover.latitude += hsteps1
                    mover.longitude += vsteps1            

            # fix order if we are on a reverse row
            if(~reverse):
                mover.latitude -= hsteps1
                mover.longitude -= vsteps1
            else:
                mover.latitude += hsteps1
                mover.longitude += vsteps1

            mover.latitude += hsteps2
            mover.longitude += vsteps2

            # add line of points to the list
            path += tempPath

            # snake the other way next time
            reverse = ~reverse

        return path


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: argv[0] {coordinate1} {c2} {c3} {c4}", file=sys.stderr)
        sys.exit(1)

    # get 4 comma-separated coordinates from input
    C1_LIST = sys.argv[1].split(',')
    C2_LIST = sys.argv[2].split(',')
    C3_LIST = sys.argv[3].split(',')

    # create coordinate objects
    USER_COORDINATE_2 = Coordinate(float(C2_LIST[0]), float(C2_LIST[1]))
    USER_COORDINATE_1 = Coordinate(float(C1_LIST[0]), float(C1_LIST[1]))
    USER_COORDINATE_3 = Coordinate(float(C3_LIST[0]), float(C3_LIST[1]))

    NAV = Navigation()
    # create path
    PATH = NAV.create_path(USER_COORDINATE_1, USER_COORDINATE_2, USER_COORDINATE_3)

    # print all coordinates
    for point in PATH:
        print(point)
