import Queue
import multiprocessing as mp

import numpy as np

from elevationmap import ElevationMap
from map import Map
from spatialutils import SpatialUtils


class VisualMagWorkforce:
    def __init__(self, elevation_map_obj, cell_resolution, origin_offset, sumator, num_workers=1, omitted_rings=0):
        self.alive = False
        self.num_workers = num_workers
        self.queue = mp.Queue()
        self.cell_resolution = cell_resolution
        self.omitted_rings = omitted_rings
        self.sumator = sumator
        self.origin_offset = origin_offset
        self.processes = []

        self.map_array = elevation_map_obj.get_map()
        self.mp_elevation_map = mp.Array("d", self.map_array.flatten())

    """
    Add a new viewpoint to the processing queue. If the viewpoint is added when the workers are running,
    there's no guarantee the point will be calculated.
    
    :param task: coordinates of the viewpoint
    """

    def add_task(self, task):
        self.queue.put(task)

    """
    Spawn the selected number of processes and begin computation.    
    """

    def start_workers(self):
        self.alive = True
        for i in range(self.num_workers):
            t = mp.Process(target=visual_mag_worker, args=(
                self.mp_elevation_map, self.map_array.shape, self.queue, self.cell_resolution, self.omitted_rings,
                self.origin_offset))
            self.processes.append(t)
            t.daemon = False
            t.start()

    """
    Wait for the workers to finish the computation of the queue. Blocking call!
    """

    def wait_to_finish(self):
        for t in self.processes:
            t.join()


"""
Calculate the visual magnitude from a viewpoint. The viewpoints are retrieved from the queue shared among processes.

:param mp_elevation_map: shared multiprocessing array containing elevation data
:param shape: shape of the array
:param cell_resolution: resolution of a cell
:param omitted_distance: distance from a viewpoint which will not be included in visual magnitude calculation
:param origin_offset: elevation offset for the viewpoints
"""


def visual_mag_worker(mp_elevation_map, shape, queue, cell_resolution, omitted_distance, origin_offset):
    print("Worker started")
    elevation_map = np.frombuffer(mp_elevation_map.get_obj()).reshape(shape)
    while not queue.empty():
        # other threads might empty the queue before this command
        try:
            origin = queue.get()
        except Queue.Empty:
            break
        origin_y = origin[0]
        origin_x = origin[1]

        los_map = Map(shape[0], shape[1], False)
        spatial = SpatialUtils(origin_y, origin_x,
                               elevation_map[origin_y, origin_x] + origin_offset,
                               cell_resolution,
                               elevation_map)

        omitted_rings, rings = ElevationMap.get_rings(origin_y, origin_x, elevation_map, omitted_distance)

        # initialize LOS value and visual magnitude of omitted rings and remove them from queue
        los_map.init_omitted_cells([[origin_y, origin_x]], Map.undefined)
        for ring in omitted_rings:
            los_map.init_omitted_cells(ring, Map.undefined)

        visible_count = invisible_count = 0  # DEBUG

        for ring in rings:
            for cell in ring:
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
                    invisible_count += 1
                else:
                    # visible
                    los_map.set(cell_y, cell_x, viewing_los)
                    visible_count += 1
                    visual_magnitude = spatial.visual_magnitude(cell_y, cell_x)
                    # sumator.add_task([cell_y, cell_x, visual_magnitude])
        print(visible_count, invisible_count)
    print("Worker starved to death")
