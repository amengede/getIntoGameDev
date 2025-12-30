from config import *

def make_spheres(count: int, material_count: int) -> np.ndarray:

    spheres = []
    for _ in range(count):
        x = np.random.uniform(low = -95.0, high = 95.0)
        y = np.random.uniform(low = -95.0, high = 95.0)
        z = np.random.uniform(low = -15.0, high = 15.0)
        radius = np.random.uniform(low = 0.3, high = 2.0)
        vx = np.random.uniform(low = -1.0, high = 1.0)
        vy = np.random.uniform(low = -1.0, high = 1.0)
        vz = np.random.uniform(low = -1.0, high = 1.0)
        material = np.random.randint(low = 0, high = material_count)
        spheres.append((x,y,z,radius,vx,vy,vz,material))

    return np.array(spheres, dtype=data_type_sphere)