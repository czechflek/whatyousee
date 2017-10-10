import numpy as np


class Map:
    undefined = -9999999

    def __init__(self, map_height, map_width, init):
        if init:
            self.map = np.zeros([map_height, map_width])
        else:
            self.map = np.empty([map_height, map_width])

    def set(self, y, x, value):
        self.map[y][x] = value

    def get(self, y, x):
        return self.map[y][x]

    def init_omitted_cells(self, omitted, value):
        for cell in omitted:
            self.map[cell[0]][cell[1]] = value

    def get_array(self):
        return self.map
