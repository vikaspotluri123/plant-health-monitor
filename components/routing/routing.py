from numpy import arange
import copy
import sys

# configuration for distance between pictures in meters
GRID_UNIT = 40

# configuration for overage margin on edge of path
MARGIN = 200

# hard code meter conversions for College Station TX
METERS_IN_DEG_LAT = 111320
METERS_IN_DEG_LON = 95789.6

# get grid unit steps in terms of lat and lon
LON_AXIS_STEP = GRID_UNIT / METERS_IN_DEG_LAT
LAT_AXIS_STEP = GRID_UNIT / METERS_IN_DEG_LON

# get overlap margins in terms of lat and lon
LONG_MARGIN = MARGIN / METERS_IN_DEG_LAT
LAT_MARGIN = MARGIN / METERS_IN_DEG_LON

# make class to store coordinates 
class Coordinate:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
    
    # this allows coordinates to be printed
    def __str__(self):
        return str(self.latitude) + ', ' + str(self.longitude)

# check if validation passes
def validateDistance(h, v):
    return abs((h**2 + v**2)**(0.5) - GRID_UNIT) < GRID_UNIT*0.15

class Navigation:

    def createPath(self, c1, c2, c3, c4):
        # calculate side1 latitude, longitude, and distance in meters
        side1lat = (c2.latitude - c1.latitude) * METERS_IN_DEG_LAT
        side1lon = (c2.longitude - c1.longitude) * METERS_IN_DEG_LON
        side1dist = (side1lat**2 + side1lon**2)**(0.5)

        # calculate side2 latitude, longitude, and distance in meters
        side2lat = (c3.latitude - c2.latitude) * METERS_IN_DEG_LAT
        side2lon = (c3.longitude - c2.longitude) * METERS_IN_DEG_LON
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
        mover = Coordinate(c1.latitude * METERS_IN_DEG_LAT + hsteps1/2 + hsteps2/2, c1.longitude * METERS_IN_DEG_LON + vsteps1/2 + vsteps2/2)
        
        # this boolean makes the snake pattern of the path
        reverse = False

        for _out in range(0,nums2):
            tempPath = []

            for _in in range(0,nums1):
                # add points to inner path for a single line
                tempPath.append(Coordinate(mover.latitude / METERS_IN_DEG_LAT, mover.longitude / METERS_IN_DEG_LON))

                if not validateDistance(hsteps1, vsteps1):
                    sys.exit("ERROR: Distance between coordinates is not within 15%% of expected value")

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

    
# get 4 comma-separated coordinates from input
userC1 = sys.argv[1].split(',')
userC2 = sys.argv[2].split(',')
userC3 = sys.argv[3].split(',')
userC4 = sys.argv[4].split(',')

# create coordinate objects
c2 = Coordinate(float(userC2[0]), float(userC2[1]))
c1 = Coordinate(float(userC1[0]), float(userC1[1]))
c3 = Coordinate(float(userC3[0]), float(userC3[1]))
c4 = Coordinate(float(userC4[0]), float(userC4[1]))

nav = Navigation()
# create path
path = nav.createPath(c1,c2,c3,c4)

# print all coordinates
for point in path:
    print(point)
