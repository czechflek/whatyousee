import time
from multiprocessing import freeze_support

from elevationmap import ElevationMap
from map import Map
from sumator import Sumator
from visualmag_workforce import VisualMagWorkforce

num_workers = 6

# TEST VALUES
origin_y = 275
origin_x = 350
omitted_rings = 0
origin_offset = 60
cell_resolution = 31
# /TEST VALUES

start_time = time.clock()

if __name__ == '__main__':
    freeze_support()

    elevation_map = ElevationMap()
    elevation_map.read_file("testData\mhkdem.tif")
    visual_magnitude_map = Map(elevation_map.get_height(), elevation_map.get_width(), True)
    sumator = Sumator(visual_magnitude_map)
    sumator.start_service()
    workforce = VisualMagWorkforce(elevation_map, cell_resolution, origin_offset, sumator, 4)

    workforce.add_task([200, 300])
    workforce.add_task([400, 300])
    workforce.add_task([300, 100])

    workforce.start_workers()
    workforce.wait_to_finish()
    sumator.stop_service()

    print("Finished in: {} s".format(time.clock() - start_time))

    # fig = plt.figure()
    # a = fig.add_subplot(1, 2, 1)
    # a.set_title("Visual Magnitude")
    # image = visual_magnitude_map.get_array()
    # norm = colors.LogNorm(clip='False')
    # im = plt.imshow(image, norm=norm)
    # plt.colorbar(im, orientation='horizontal')
    #
    # c = fig.add_subplot(1, 2, 2)
    # c.set_title("Elevation map")
    # image3 = elevation_map.get_map()
    # im3 = plt.imshow(image3, cmap='hot')
    # plt.colorbar(im3, orientation='horizontal')
    #
    # plt.suptitle("Viewpoint [{}, {}] with elevation offset {}".format(origin_x, origin_y, origin_offset))
    # plt.show()
