import cv2
import numpy as np


class ElevationMap:
    def __init__(self):
        self.loaded = False
        self.map = None

    def read_file(self, filename):
        self.map = cv2.imread(filename, -1)
        self.loaded = True

    """
    Generate a rectangle around the specified coordinates in the provided distance.
    
    :param y: Y coordinate of the viewpoint
    :param x: X coordinate of the viewpoint
    :param distance: distance or step from the viewpoint
    :returns: list of triplets (y, x, elevation) for each point on the ring 
    """

    def get_ring(self, y, x, distance):
        # calculate boundaries
        inbounds = {'tl': True, 'tr': True, 'br': True, 'bl': True}

        tl = [y - distance, x - distance]  # top-left corner
        if tl[0] < 0:
            tl[0] = 0
            inbounds['tl'] = False
        if tl[1] < 0:
            tl[1] = 0

        tr = [y - distance, x + distance]  # top-right corner
        if tr[0] < 0:
            tr[0] = 0
        if tr[1] >= self.map.shape[1]:
            tr[1] = self.map.shape[1] - 1
            inbounds['tr'] = False

        br = [y + distance, x + distance]  # bottom-right corner
        if br[0] >= self.map.shape[0]:
            br[0] = self.map.shape[0] - 1
            inbounds['br'] = False
        if br[1] >= self.map.shape[1]:
            br[1] = self.map.shape[1] - 1

        bl = [y + distance, x - distance]  # bottom-left corner
        if bl[0] >= self.map.shape[0]:
            bl[0] = self.map.shape[0] - 1
        if bl[1] < 0:
            bl[0] = 0
            inbounds['bl'] = False

        # create a list of ring coordinates
        ring = []
        # print("Ring bounds {}: {}, {}, {}, {}".format(distance, tl, tr, br, bl))

        if inbounds['tl']:
            for x in np.arange(tl[1], tr[1]):
                ring.append((tl[0], x, self.map.item(tl[0], x)))

        if inbounds['tr']:
            for y in np.arange(tr[0], br[0]):
                ring.append((y, tr[1], self.map.item(y, tr[1])))

        if inbounds['br']:
            for x in np.arange(br[1], bl[1], -1):
                ring.append((br[0], x, self.map.item(br[0], x)))

        if inbounds['bl']:
            for y in np.arange(bl[0], tl[0], -1):
                ring.append((y, bl[1], self.map.item(y, bl[1])))

        # print("Ring with distance {} contains {} points\n".format(distance, len(ring)))
        return ring

    def get_neighborhood(self, y, x):
        neighborhood = np.empty([3, 3])
        for i in np.arange(-1, 2):
            for j in np.arange(-1, 2):
                try:
                    neighborhood[i + 1][j + 1] = self.map[y + i][x + j]
                except IndexError:
                    neighborhood[i + 1][j + 1] = float(0)
        return neighborhood

    def get_height(self):
        return self.map.shape[0]

    def get_width(self):
        return self.map.shape[1]

    def get_elevation(self, y, x):
        return self.map[y][x]

    def get_map(self):
        return self.map
