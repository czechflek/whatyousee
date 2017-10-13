import time
from multiprocessing import freeze_support

import matplotlib.pyplot as plt
from matplotlib import colors

from elevationmap import ElevationMap
from visualmag_workforce import VisualMagWorkforce

num_workers = 6

# TEST VALUES
origin_y = 275
origin_x = 350
omitted_rings = 0
origin_offset = 1.8
cell_resolution = 31
# /TEST VALUES

start_time = time.clock()

if __name__ == '__main__':
    freeze_support()

    elevation_map = ElevationMap()
    elevation_map.read_map_file("testData\mhkdem.tif")
    workforce = VisualMagWorkforce(elevation_map, cell_resolution, origin_offset, 10)

    viewpoints = elevation_map.read_viewpoints("testData\path2.tif")

    print("Calculating {} viewpoints".format(len(viewpoints)))
    for vp in viewpoints:
        workforce.add_task(vp)

    print("Initialization finished in: {} s".format(time.clock() - start_time))

    start_time = time.clock()

    workforce.start_workers()
    visual_magnitude = workforce.get_sumator_pipe().recv()

    print("Calculation in: {} s".format(time.clock() - start_time))

    fig = plt.figure()
    a = fig.add_subplot(1, 2, 1)
    a.set_title("Visual Magnitude")
    image = visual_magnitude
    norm = colors.LogNorm(clip='False')
    im = plt.imshow(image, norm=norm)
    plt.colorbar(im, orientation='horizontal')

    c = fig.add_subplot(1, 2, 2)
    c.set_title("Elevation map")
    image3 = elevation_map.get_map()
    im3 = plt.imshow(image3, cmap='hot')
    plt.colorbar(im3, orientation='horizontal')

    plt.suptitle("Viewpoint [{}, {}] with elevation offset {}".format(origin_x, origin_y, origin_offset))
    plt.show()
