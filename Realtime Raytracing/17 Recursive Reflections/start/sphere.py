from config import *

def make_spheres(count: int) -> np.ndarray:

    spheres = np.zeros(8 * count,dtype = np.float32)
    for i in range(count):
        base_index = 8 * i
        #x
        spheres[base_index] = np.random.uniform(low = -95.0, high = 95.0)
        #y
        spheres[base_index + 1] = np.random.uniform(low = -95.0, high = 95.0)
        #z
        spheres[base_index + 2] = np.random.uniform(low = -15.0, high = 15.0)
        #radius
        spheres[base_index + 3] = np.random.uniform(low = 0.3, high = 2.0)
        #r
        spheres[base_index + 4] = np.random.uniform(low = 0.0, high = 1.0)
        #g
        spheres[base_index + 5] = np.random.uniform(low = 0.0, high = 1.0)
        #b
        spheres[base_index + 6] = np.random.uniform(low = 0.0, high = 1.0)
        #roughness
        spheres[base_index + 7] = np.random.uniform(low = 0.0, high = 1.0)

    return spheres