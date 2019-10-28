from numpy import arange
import matplotlib.pyplot as plt
import copy

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
        return "[" + str(self.latitude) + ', ' + str(self.longitude) + '],'

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
        reverseLong = False

        nums1 = len(arange(0, side1dist, GRID_UNIT))
        hsteps1 = side1lat / nums1
        vsteps1 = side1lon / nums1

        nums2 = len(arange(0, side2dist, GRID_UNIT))
        hsteps2 = side2lat / nums2
        vsteps2 = side2lon / nums2

        #print(nums1, nums2)

        #path.append(Coordinate(mover.latitude / METERS_IN_DEG_LAT, mover.longitude / METERS_IN_DEG_LON))
        reverse = False

        for _out in range(0,nums2):
            tempPath = []


            for _in in range(0,nums1):
                #print(ignoreme, ignoreme2)

                tempPath.append(Coordinate(mover.latitude / METERS_IN_DEG_LAT, mover.longitude / METERS_IN_DEG_LON))

                if reverse:
                    mover.latitude -= hsteps1
                    mover.longitude -= vsteps1
                else:
                    mover.latitude += hsteps1
                    mover.longitude += vsteps1
            
            

            #for ob in tempPath:
                #print(ob)
            

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






        """for (x, y) in (arange(c1 + side1lat-LAT_MARGIN, c1.latitude+LAT_MARGIN, LAT_AXIS_STEP)):
            tempPath = []
            for lon in arange(c1.longitude-LONG_MARGIN, c2.longitude+LONG_MARGIN, LON_AXIS_STEP):
                temppath.append(Coordinate(lat, lon))
            
            else:
                for lon in arange(c2.longitude+LONG_MARGIN, c1.longitude-LONG_MARGIN, -LON_AXIS_STEP):
                    path.append(Coordinate(lat, lon))
            reverseLong = not reverseLong
        """


        return path



c1 = Coordinate(30.55558, -96.40986)
c2 = Coordinate(30.55592, -96.40877)
c3 = Coordinate(30.55360, -96.40781)
c4 = Coordinate(30.55326, -96.40890)


nav = Navigation()
path = nav.createPath(c1,c2,c3,c4)

#for point in path:
    #print(point)

x = []
y = []

for point in path:
    x.append(point.latitude)
    y.append(point.longitude)

    print(point)

#plt.scatter(x,y)
#plt.show()