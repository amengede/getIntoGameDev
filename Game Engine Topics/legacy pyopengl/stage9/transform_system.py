from config import *

class TransformSystem:

    def update(self, plane_thetas: np.ndarray) -> None:

        for i in range(len(plane_thetas)):
            plane_thetas[i] += 1
            if plane_thetas[i] > 360:
                plane_thetas[i] -= 360
