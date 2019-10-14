from numpy import arange

LONG_STEP = 0.25
LAT_STEP = 0.25


class Coordinate:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
    
    def __str__(self):
        return "(" + str(self.latitude) + ', ' + str(self.longitude) + ')'

class Navigation:
    def createPath(self, c1, c2, c3, c4):
        path = []
        reverseLong = False

        for lat in arange(c3.latitude, c1.latitude, LAT_STEP):
            for lon in arange(c1.longitude, c2.longitude, LONG_STEP):
                if not reverseLong:
                    path.append(Coordinate(lat, lon))
                else:
                    path.append(Coordinate(lat, c2 - lon))
        
        return path



c1 = Coordinate(1.0000000, 0.0000000)
c2 = Coordinate(1.0000000, 1.0000000)
c3 = Coordinate(0.0000000, 1.0000000)
c4 = Coordinate(0.0000000, 0.0000000)


nav = Navigation()
path = nav.createPath(c1,c2,c3,c4)

for point in path:
    print(point)
