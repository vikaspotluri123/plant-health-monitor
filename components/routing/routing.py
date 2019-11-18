from numpy import arange
import copy
import sys

# configuration for distance between pictures in meters
GRID_UNIT = 40

# configuration for overage margin on edge of path
MARGIN = 20

METERS_IN_DEG_LAT = 111320
METERS_IN_DEG_LON = 95789.6

LON_AXIS_STEP = GRID_UNIT / METERS_IN_DEG_LAT
LAT_AXIS_STEP = GRID_UNIT / METERS_IN_DEG_LON

LONG_MARGIN = MARGIN / METERS_IN_DEG_LAT
LAT_MARGIN = MARGIN / METERS_IN_DEG_LON

class Coordinate:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
    
    def __str__(self):
        return str(self.latitude) + ', ' + str(self.longitude)

class Navigation:
    def createPath(self, c1, c2, c3, c4):
        mover = Coordinate(c1.latitude * METERS_IN_DEG_LAT, c1.longitude * METERS_IN_DEG_LON)

        side1lat = (c2.latitude - c1.latitude) * METERS_IN_DEG_LAT
        side1lon = (c2.longitude - c1.longitude) * METERS_IN_DEG_LON
        side1dist = (side1lat**2 + side1lon**2)**(0.5)

        side2lat = (c3.latitude - c2.latitude) * METERS_IN_DEG_LAT
        side2lon = (c3.longitude - c2.longitude) * METERS_IN_DEG_LON
        side2dist = (side2lat**2 + side2lon**2)**(0.5)

        path = []

        nums1 = len(arange(0, side1dist, GRID_UNIT))
        hsteps1 = side1lat / nums1
        vsteps1 = side1lon / nums1

        nums2 = len(arange(0, side2dist, GRID_UNIT))
        hsteps2 = side2lat / nums2
        vsteps2 = side2lon / nums2
        
        reverse = False

        for _out in range(0,nums2):
            tempPath = []


            for _in in range(0,nums1):
                tempPath.append(Coordinate(mover.latitude / METERS_IN_DEG_LAT, mover.longitude / METERS_IN_DEG_LON))

                if reverse:
                    mover.latitude -= hsteps1
                    mover.longitude -= vsteps1
                else:
                    mover.latitude += hsteps1
                    mover.longitude += vsteps1            

            if(~reverse):
                mover.latitude -= hsteps1
                mover.longitude -= vsteps1
            else:
                mover.latitude += hsteps1
                mover.longitude += vsteps1

            mover.latitude += hsteps2
            mover.longitude += vsteps2

            path += tempPath

            reverse = ~reverse

        return path

    
    
userC1 = sys.argv[1].split(',')
userC2 = sys.argv[2].split(',')
userC3 = sys.argv[3].split(',')
userC4 = sys.argv[4].split(',')

c2 = Coordinate(float(userC2[0]), float(userC2[1]))
c1 = Coordinate(float(userC1[0]), float(userC1[1]))
c3 = Coordinate(float(userC3[0]), float(userC3[1]))
c4 = Coordinate(float(userC4[0]), float(userC4[1]))

print(c1)

nav = Navigation()
path = nav.createPath(c1,c2,c3,c4)

x = []
y = []

for point in path:
    x.append(point.latitude)
    y.append(point.longitude)

    print(point)
