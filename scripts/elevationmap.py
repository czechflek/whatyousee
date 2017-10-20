import numpy as np
import arcpy


class ElevationMap:
    def __init__(self):
        self.loaded = False
        self.map = None
        self.cell_resolution = 0

    def read_map_file(self, raster):
        arcpy.AddMessage("Raster: {}".format(raster))
        self.map = arcpy.RasterToNumPyArray(raster)

        props = arcpy.GetRasterProperties_management(raster, "CELLSIZEX")
        self.cell_resolution = float(props.getOutput(0))

        self.loaded = True

    @staticmethod
    def read_viewpoints(raster):
        path = arcpy.RasterToNumPyArray(raster)
        viewpoints = []
        for y in range(path.shape[0]):
            for x in range(path.shape[1]):
                if path[y][x] > 0:
                    viewpoints.append([y, x, path[y][x]])
        return viewpoints

    """
    Generate rectangles around the specified coordinates. Specify the distance to be excluded from the results.
    
    :param y: Y coordinate of the viewpoint
    :param x: X coordinate of the viewpoint
    :param map_array: numpy array which contains elevation data
    :param omitted_distance: distance which will be excluded from results
    :returns: list of omitted rings and list of rings to be solved
    """

    @staticmethod
    def get_rings(y, x, map_array, omitted_distance):
        omitted_rings = []
        rings = []
        # calculate the excluded rings
        for distance in range(1, omitted_distance + 1):
            ring = ElevationMap.__get_ring(y, x, map_array, distance)
            omitted_rings.append(ring)

        # calculate the rings to be solved
        distance = omitted_distance + 1
        ring = ElevationMap.__get_ring(y, x, map_array, distance)
        while len(ring):
            rings.append(ring)
            ring = ElevationMap.__get_ring(y, x, map_array, distance)
            distance += 1

        len
        return omitted_rings, rings

    """
    Generate a rectangle around the specified coordinates in the provided distance.
    
    :param y: Y coordinate of the viewpoint
    :param x: X coordinate of the viewpoint
    :param map_array: numpy array which contains elevation data
    :param distance: distance or step from the viewpoint
    :returns: list of triplets (y, x, elevation) for each point on the ring 
    """

    @staticmethod
    def __get_ring(y, x, map_array, distance):
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
        if tr[1] >= map_array.shape[1]:
            tr[1] = map_array.shape[1] - 1
            inbounds['tr'] = False

        br = [y + distance, x + distance]  # bottom-right corner
        if br[0] >= map_array.shape[0]:
            br[0] = map_array.shape[0] - 1
            inbounds['br'] = False
        if br[1] >= map_array.shape[1]:
            br[1] = map_array.shape[1] - 1

        bl = [y + distance, x - distance]  # bottom-left corner
        if bl[0] >= map_array.shape[0]:
            bl[0] = map_array.shape[0] - 1
        if bl[1] < 0:
            bl[0] = 0
            inbounds['bl'] = False

        # create a list of ring coordinates
        ring = []
        # print("Ring bounds {}: {}, {}, {}, {}".format(distance, tl, tr, br, bl))

        if inbounds['tl']:
            for x in np.arange(tl[1], tr[1]):
                ring.append((tl[0], x, map_array.item(tl[0], x)))

        if inbounds['tr']:
            for y in np.arange(tr[0], br[0]):
                ring.append((y, tr[1], map_array.item(y, tr[1])))

        if inbounds['br']:
            for x in np.arange(br[1], bl[1], -1):
                ring.append((br[0], x, map_array.item(br[0], x)))

        if inbounds['bl']:
            for y in np.arange(bl[0], tl[0], -1):
                ring.append((y, bl[1], map_array.item(y, bl[1])))

        # print("Ring with distance {} contains {} points\n".format(distance, len(ring)))
        return ring

    def get_height(self):
        return self.map.shape[0]

    def get_width(self):
        return self.map.shape[1]

    def get_elevation(self, y, x):
        return self.map[y][x]

    def get_map(self):
        return self.map

    def get_cell_resolution(self):
        return self.cell_resolution
