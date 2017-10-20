import arcpy
import time
from multiprocessing import freeze_support, set_executable

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
    dem = str(arcpy.GetParameter(0)).replace("\\", "/")
    viewpoint_map = str(arcpy.GetParameter(1)).replace("\\", "/")
    origin_offset = arcpy.GetParameter(2)
    omitted_rings = arcpy.GetParameter(3)
    processes = arcpy.GetParameter(4)

    elevation_map = ElevationMap()
    elevation_map.read_map_file(dem)
    workforce = VisualMagWorkforce(elevation_map, origin_offset, processes)

    viewpoints = elevation_map.read_viewpoints(viewpoint_map)

    arcpy.AddMessage("Calculating {} viewpoints".format(len(viewpoints)))
    for vp in viewpoints:
        workforce.add_task(vp)

    arcpy.AddMessage("Initialization finished in: {} s".format(time.clock() - start_time))

    start_time = time.clock()

    workforce.start_workers()
    visual_magnitude = workforce.get_sumator_pipe().recv()

    arcpy.AddMessage("Calculation in: {} s".format(time.clock() - start_time))

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
