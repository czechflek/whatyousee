import numpy as np


def sumator(connections, main_pipe, shape):
    visual_magnitude = np.zeros(shape, "d")
    received_objects = 0
    active_conns = len(connections)
    print(active_conns)
    while active_conns > 0:
        for conn in connections:
            if conn.poll():
                data = conn.recv()
                if data is None:
                    active_conns -= 1
                else:
                    visual_magnitude[data[0]][data[1]] += data[2]
                    received_objects += 1

    # clean up, return the results to the main process and die
    for conn in connections:
        conn.close()
    main_pipe.send(visual_magnitude)
    print("Received {} results".format(received_objects))
