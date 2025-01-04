from config import *

def make_spheres(count: int) -> np.ndarray:

    spheres = np.zeros(count, dtype = DATA_TYPE_SPHERE)
    for i in range(count):

        new_sphere = np.zeros(1, DATA_TYPE_SPHERE)
        
        new_sphere[0]['x'] = np.random.uniform(low = -95.0, high = 95.0)
        new_sphere[0]['y'] = np.random.uniform(low = -95.0, high = 95.0)
        new_sphere[0]['z'] = np.random.uniform(low = -15.0, high = 15.0)
        new_sphere[0]['radius'] = np.random.uniform(low = 0.3, high = 2.0)
        new_sphere[0]['r'] = np.random.uniform(low = 0.0, high = 1.0)
        new_sphere[0]['g'] = np.random.uniform(low = 0.0, high = 1.0)
        new_sphere[0]['b'] = np.random.uniform(low = 0.0, high = 1.0)
        new_sphere[0]['reflectance'] = np.random.uniform(low = 0.2, high = 0.8)
        new_sphere[0]['eta'] = np.random.uniform(low = 0.5, high = 0.9)

        spheres[i] = new_sphere[0]

    return spheres