import collections as c

import numpy as np
import time
from matplotlib import colors, pyplot as plt

from elevationmap import ElevationMap
from map import Map
from spatialutils import SpatialUtils

num_workers = 6

# TEST VALUES
origin_y = 275
origin_x = 350
omitted_rings = 0
origin_offset = 60
cell_resolution = 31
# /TEST VALUES

elevation_map = ElevationMap()
elevation_map.read_file("testData\mhkdem.tif")
los_map = Map(elevation_map.get_height(), elevation_map.get_width())
visual_magnitude_map = Map(elevation_map.get_height(), elevation_map.get_width())
spatial = SpatialUtils(origin_y, origin_x, elevation_map.get_elevation(origin_y, origin_x) + origin_offset,
                       cell_resolution,
                       elevation_map)

# create a thread-safe queue of all rings
i = 1
rings_queue = c.deque()
ring = elevation_map.get_ring(origin_y, origin_x, i)
while len(ring) and i < 1000000:
    rings_queue.appendleft(c.deque(ring))
    i += 1
    ring = elevation_map.get_ring(origin_y, origin_x, i)

# initialize LOS value and visual magnitude of omitted rings and remove them from queue
los_map.init_omitted_cells([[origin_y, origin_x]], Map.undefined)
visual_magnitude_map.init_omitted_cells([[origin_y, origin_y]], 0)

for i in np.arange(0, omitted_rings):
    ring = rings_queue.pop()
    los_map.init_omitted_cells(ring, Map.undefined)
    visual_magnitude_map.init_omitted_cells(ring, 0)

visible_count = invisible_count = 0  # DEBUG

while rings_queue:
    cell_queue = rings_queue.pop()
    while cell_queue:
        cell = cell_queue.pop()
        cell_y = cell[0]
        cell_x = cell[1]

        # calculate viewing LOS of the cell and interpolated LOS of the point directly in front of the cell
        interpolated_weight = spatial.interpolate_weight(cell_y, cell_x)
        los_cells = spatial.get_los_cells(cell_y, cell_x)
        adjacent_los = los_map.get(los_cells["adjacent"][0], los_cells["adjacent"][1]) * interpolated_weight
        offset_los = los_map.get(los_cells["offset"][0], los_cells["offset"][1]) * (1 - interpolated_weight)
        # print(adjacent_los, offset_los)

        viewing_los = spatial.get_viewing_slope(cell_y, cell_x)
        cell_los = adjacent_los + offset_los
        # print(viewing_los, cell_los)

        if viewing_los < cell_los:
            # not visible
            los_map.set(cell_y, cell_x, cell_los)
            visual_magnitude_map.set(cell_y, cell_x, 0)
            invisible_count += 1
        else:
            # visible
            los_map.set(cell_y, cell_x, viewing_los)
            visible_count += 1
            visual_magnitude = spatial.visual_magnitude(cell_y, cell_x)
            visual_magnitude_map.set(cell_y, cell_x, visual_magnitude)
            # print("{}:{} = {}".format(cell_y, cell_x, visual_magnitude))

total_time = time.clock() - start_time
print(visible_count, invisible_count, visible_count + invisible_count)  # DEBUG

"""
fig = plt.figure()
a = fig.add_subplot(1, 3, 1)
a.set_title("Visual Magnitude")
image = visual_magnitude_map.get_array()
norm = colors.LogNorm(clip='False')
im = plt.imshow(image, norm=norm)
plt.colorbar(im, orientation='horizontal')

b = fig.add_subplot(1, 3, 2)
b.set_title("LOS")
image2 = los_map.get_array()
low_values = image2 < -3
image2[low_values] = -3
im2 = plt.imshow(image2, cmap='hot')
plt.colorbar(im2, orientation='horizontal')

c = fig.add_subplot(1, 3, 3)
c.set_title("Elevation map")
image3 = elevation_map.get_map()
im3 = plt.imshow(image3, cmap='hot')
plt.colorbar(im3, orientation='horizontal')

plt.suptitle("Viewpoint [{}, {}] with elevation offset {}".format(origin_x, origin_y, origin_offset))
plt.show()
"""
