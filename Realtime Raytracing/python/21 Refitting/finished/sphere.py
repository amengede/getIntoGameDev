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

@njit(cache = True)
def update_spheres(spheres: np.ndarray, dt: float) -> None:

    for i in range(len(spheres)):

        sx = spheres[i]['x']
        sy = spheres[i]['y']
        sz = spheres[i]['z']

        vx = spheres[i]['vx']
        vy = spheres[i]['vy']
        vz = spheres[i]['vz']

        #Check for rebounds
        if sx < -95.0 or sx > 95.0:
            vx = vx * -1
        if sy < -95.0 or sy > 95.0:
            vy = vy * -1
        if sz < -15.0 or sz > 15.0:
            vz = vz * -1
        
        #Update positions and velocities
        spheres[i]['x'] = sx + dt * vx
        spheres[i]['y'] = sy + dt * vy
        spheres[i]['z'] = sz + dt * vz

        spheres[i]['vx'] = vx
        spheres[i]['vy'] = vy
        spheres[i]['vz'] = vz