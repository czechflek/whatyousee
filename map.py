import numpy as np


class Map:
    undefined = -9999999

    def __init__(self, map_height, map_width):
        self.los_map = np.empty([map_height, map_width])

    def set(self, y, x, value):
        self.los_map[y][x] = value

    def get(self, y, x):
        return self.los_map[y][x]

    def init_omitted_cells(self, omitted, value):
        for cell in omitted:
            self.los_map[cell[0]][cell[1]] = value

    def get_array(self):
        return self.los_map
