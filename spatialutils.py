import math

import numpy as np


class SpatialUtils:
    light_refraction = 0.13
    pi_pul = math.pi / 2

    def __init__(self, origin_y, origin_x, origin_elevation, cell_resolution, elevation_map, ):
        self.origin_y = origin_y
        self.origin_x = origin_x
        self.origin_elevation = origin_elevation
        self.cell_resolution = cell_resolution
        self.elevation_map = elevation_map

    """
    Calculate visual magnitude of the cell relative to the origin.
    
    :param cell_y: y coordinate of the cell
    :param cell_x: x coordinate of the cell
    
    :returns: visual magnitude value
    """

    def visual_magnitude(self, cell_y, cell_x):
        distance = self.__get_distance(cell_y, cell_x)
        cell_slope = self.__get_cell_slope(cell_y, cell_x)
        viewing_slope = self.get_viewing_slope(cell_y, cell_x)
        cell_aspect = self.__get_cell_aspect(cell_y, cell_x)
        viewing_aspect = self.__get_viewing_aspect(cell_y, cell_x)

        view_vector = self.__make_directional_vector(viewing_aspect, viewing_slope)
        cell_normal = self.__make_directional_vector(cell_aspect, cell_slope)

        vector_angle = self.__get_angle_difference(view_vector, cell_normal)

        if vector_angle <= SpatialUtils.pi_pul:
            return 0  # the plane is not visible

        visual_magnitude = pow(self.cell_resolution, 2) / pow(distance, 2)
        visual_magnitude *= abs(math.cos(vector_angle))

        return visual_magnitude

    """
    Calculate the angle from origin to the specified point. The angle is compensated for Earth's curvature and light 
    diffraction.
        
    :param y: y coordinate of the cell
    :param x: x coordinate of the cell
    :param elevation: elevation of the point
    :param light_refraction: (optional) refraction index of the atmosphere
    
    :returns: Vertical angle from origin to the specified point in degrees relative to horizon. 
    """

    def get_viewing_slope(self, y, x):
        dist_y, dist_x, elevation_diff = self.__get_yxz_differences(y, x)
        direct_distance = math.sqrt(pow(dist_x, 2) + pow(dist_y, 2))

        return math.degrees(math.atan2(elevation_diff, direct_distance))

    """
    Calculate cell slope.
    
    Ref to Shi, Zhu, Burt, et al. (2007), An Experiment Using a Circular Neighborhood to Calculate Slope Gradient 
    from a DEM, PHOTOGRAMMETRIC ENGINEERING & REMOTE SENSING, (2) 143-154.
    
    :param cell_y: y coordinate of the cell
    :param cell_x: x coordinate of the cell
    
    :returns: cell slope in degrees
    """

    def __get_cell_slope(self, cell_y, cell_x):
        westeast, northsouth = self.__get_cell_slope_components(cell_y, cell_x)

        return math.degrees(math.sqrt(pow(westeast, 2) + pow(northsouth, 2)))

    """
    Calculate cell aspect. 0 = North, 90 = East, 180 = South, 270 = Westt
    
    :param cell_y: y coordinate of the cell
    :param cell_x: x coordinate of the cell
    
    :returns: cell aspect in degrees or -1 if the surface is flat
    """

    def __get_cell_aspect(self, cell_y, cell_x):
        westeast, northsouth = self.__get_cell_slope_components(cell_y, cell_x)

        return (math.degrees(math.atan2(-1 * northsouth, -1 * westeast)) + 630) % 360

    """
    Calculate the weight of the cell adjacent to the current one.
    
    :param y: y coordinate of the cell
    :param x: x coordinate of the cell
    :returns: weight of the cell
    """

    def interpolate_weight(self, y, x):
        neighbors = self.get_los_cells(y, x)
        cell_angle = self.__get_viewing_aspect(y, x)
        adjacent_angle = self.__get_viewing_aspect(neighbors["adjacent"][0], neighbors["adjacent"][1])
        offset_angle = self.__get_viewing_aspect(neighbors["offset"][0], neighbors["offset"][1])
        total = abs(adjacent_angle - cell_angle) + abs(offset_angle - cell_angle)
        if total == 0:
            return 1
        else:
            return abs(offset_angle - cell_angle) / total

    """
    Get the neighborhood cells in the line of sight based on a orientation code. 

    :param y: y coordinate of the cell
    :param x: x coordinate of the cell

    :returns: Array of two tuples (y, x) with location index offsets
    """

    def get_los_cells(self, y, x):
        code = self.__get_orientation(y, x)
        index_offsets = {
            0x0020: [(0, 1), (0, 1)],
            0x0100: [(0, 1), (1, 1)],
            0x1200: [(1, 1), (1, 1)],
            0x0000: [(1, 0), (1, 1)],
            0x0002: [(1, 0), (1, 0)],
            0x0001: [(1, 0), (1, -1)],
            0x2101: [(1, -1), (1, -1)],
            0x1001: [(0, -1), (1, -1)],
            0x0021: [(0, -1), (0, -1)],
            0x1011: [(0, -1), (-1, -1)],
            0x1211: [(-1, -1), (-1, -1)],
            0x1111: [(-1, 0), (-1, -1)],
            0x0012: [(-1, 0), (-1, 0)],
            0x1110: [(-1, 0), (-1, 1)],
            0x2110: [(-1, 1), (-1, 1)],
            0x0110: [(0, 1), (-1, 1)]
        }.get(code, None)
        return {"adjacent": [y + index_offsets[0][0], x + index_offsets[0][1]],
                "offset": [y + index_offsets[1][0], x + index_offsets[1][1]]}

    """
    Calculate an orientation code relative to the origin.
    
    TODO: substitute the method with angle calculation
    
    Codes (clockwise):
        0x0020 = left half of the x-axis
        0x0100 = left diagonal half of the top-left quadrant
        0x1200 = top-left diagonal
        0x0000 = right diagonal half of the top-left quadrant
        0x0002 = top half of y-axis
        0x0001 = left diagonal half of the top-right quadrant        
        0x2101 = top-right diagonal
        0x1001 = right diagonal half of the top-right quadrant   
        0x0021 = right half of x-axis
        0x1011 = right diagonal half of the bottom-right quadrant
        0x1211 = bottom-right diagonal
        0x1111 = left diagonal half of the bottom-right quadrant 
        0x0012 = bottom half of y-axis
        0x1110 = right diagonal half of the bottom-left quadrant
        0x2110 = bottom-right diagonal
        0x0110 = left diagonal half of the bottom-left quadrant 
    :param y: y coordinate
    :param x: x coordinate
    
    :returns: orientation code
    """

    def __get_orientation(self, y, x):
        relative_x = x - self.origin_x
        relative_y = y - self.origin_y
        orientation = 0

        if relative_x > 0:
            orientation = 0x0001
        elif relative_x == 0:
            orientation = 0x0002

        if relative_y > 0:
            orientation += 0x0010
        elif relative_y == 0:
            orientation += 0x0020

        if relative_x == relative_y:
            orientation += 0x1200
        elif relative_x == -relative_y:
            orientation += 0x2100
        elif not (relative_x == 0 or relative_y == 0):
            if relative_y > relative_x:
                orientation += 0x0100
            if relative_y > -relative_x:
                orientation += 0x1000
        return orientation

    """
    Get the angle in degrees at which the cell is viewed. 
    North = 0, East = 90, South = 180, West = 270
    
    :param y: y coordinate of the cell
    :param x: x coordinate of the cell
    :returns: angle to the cell
    """

    def __get_viewing_aspect(self, y, x):
        aspect = math.degrees(
            math.atan2((y - self.origin_y) * self.cell_resolution, (x - self.origin_x) * self.cell_resolution))
        return (aspect + 450) % 360

    """
    Calculate 3D distance between origin and the cell.
    
    :param y: y coordinate of the cell
    :param x: x coordinate of the cell
    
    :return: distance from origin to the cell
    """

    def __get_distance(self, y, x):
        dist_y, dist_x, dist_z = self.__get_yxz_differences(y, x)

        return math.sqrt(pow(dist_x, 2) + pow(dist_y, 2) + pow(dist_z, 2))

    """
    Calculate difference between origin and cell for y, x coordinates and elevation adjusted for Earth's curvature.
    
    :param y: y coordinate of the cell
    :param x: x coordinate of the cell
    
    :return: y-distance, x-distance, elevation difference
    """

    def __get_yxz_differences(self, y, x):
        elevation = self.elevation_map.get_elevation(y, x)
        dist_y = abs(self.origin_y - y) * self.cell_resolution
        dist_x = abs(self.origin_x - x) * self.cell_resolution

        direct_distance = math.sqrt(pow(dist_x, 2) + pow(dist_y, 2))
        curvature = pow(direct_distance, 2) / 12740000

        elevation_diff = elevation - curvature + SpatialUtils.light_refraction * curvature - self.origin_elevation

        return dist_y, dist_x, elevation_diff

    """
    Calculate East-West and North-South components of the cell slope.
    
    :param cell_y: y coordinate of the cell
    :param cell_x: x coordinate of the cell
    
    :returns: East-West and North-South components
    """

    def __get_cell_slope_components(self, cell_y, cell_x):
        hood = self.elevation_map.get_neighborhood(cell_y, cell_x)
        """
        hood[0][0] = 2
        hood[0][1] = 2
        hood[0][2] = 2
        hood[1][0] = 1
        hood[1][1] = 1
        hood[1][2] = 1
        hood[2][0] = 0
        hood[2][1] = 0
        hood[2][2] = 0
        """
        cn = math.sqrt(2)
        # TODO: Border cases
        westeast = ((cn * hood[0][0] + hood[1][0] + hood[2][0])
                    - (cn * hood[0][2] + hood[1][2] + hood[2][2])) / 8 * self.cell_resolution
        northsouth = ((cn * hood[0][0] + hood[0][1] + hood[0][2]) -
                      (cn * hood[2][0] + hood[2][1] + hood[2][2])) / 8 * self.cell_resolution
        return westeast, northsouth

    """
    Create a vector representation of two angles - azimuth and slope.
    
    :param azimuth: azimuth (horizontal angle)
    :param slope: slope (vertical angle)
    
    :returns: 3D vector 
    """

    @staticmethod
    def __make_directional_vector(azimuth, slope):
        x = math.sin(math.radians(azimuth)) * math.cos(math.radians(slope))
        y = math.sin(math.radians(azimuth)) * math.sin(math.radians(slope))
        z = math.cos(math.radians(slope))
        return [x, y, z]

    """
    Calculate the angle between two vectors.
    
    :param view_vector: vector from the origin
    :param cell_normal: normal vector of the cell
    
    :returns: angle between the two vectors 
    """

    @staticmethod
    def __get_angle_difference(view_vector, cell_normal):
        normalized_view_vector = view_vector / np.linalg.norm(view_vector)
        normalized_cell_normal = cell_normal / np.linalg.norm(cell_normal)

        return math.acos(np.dot(normalized_view_vector, normalized_cell_normal))
