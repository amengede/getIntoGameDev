from config import *

def make_spheres(count: int) -> np.ndarray:

    spheres = np.zeros(SPHERE_STRIDE * count,dtype = np.float32)
    for i in range(count):
        index = SPHERE_STRIDE * i
        spheres[index + SPHERE_ATTRIBUTE_X] = np.random.uniform(low = -95.0, high = 95.0)
        spheres[index + SPHERE_ATTRIBUTE_Y] = np.random.uniform(low = -95.0, high = 95.0)
        spheres[index + SPHERE_ATTRIBUTE_Z] = np.random.uniform(low = -15.0, high = 15.0)
        spheres[index + SPHERE_ATTRIBUTE_RADIUS] = np.random.uniform(low = 0.3, high = 2.0)
        spheres[index + SPHERE_ATTRIBUTE_R] = np.random.uniform(low = 0.0, high = 1.0)
        spheres[index + SPHERE_ATTRIBUTE_G] = np.random.uniform(low = 0.0, high = 1.0)
        spheres[index + SPHERE_ATTRIBUTE_B] = np.random.uniform(low = 0.0, high = 1.0)
        spheres[index + SPHERE_ATTRIBUTE_REFLECTANCE] = np.random.uniform(low = 0.2, high = 0.8)
        #spheres[index + SPHERE_ATTRIBUTE_ETA] = np.random.uniform(low = 1.0, high = 2.0)

    return spheres