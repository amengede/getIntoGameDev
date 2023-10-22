from config import *
import sphere
import camera
import node
import bvh_backend

class Scene:
    """
        Holds pointers to all objects in the scene
    """


    def __init__(self):
        """
            Set up scene objects.
        """
        
        
        sphere_count = 3000
        self.spheres = sphere.make_spheres(sphere_count)
        
        self.camera = camera.Camera(
            position = [0.0, 0.0, 1.0]
        )

        self.sphere_ids = np.arange(sphere_count, dtype=np.int32)

        self.nodes = node.make_nodes(2 * sphere_count + 1)

        start = time.time()
        self.nodes_used = bvh_backend.build_bvh(
            self.nodes, self.spheres, self.sphere_ids, sphere_count)
        finish = time.time()
        print(f"BVH build took {(finish - start) * 1000} ms.")

        self.outDated = True
    
    def rebuild(self):

        self.nodes_used = bvh_backend.build_bvh(
            self.nodes, self.spheres, self.sphere_ids, 3000)
    
    def move_player(self, forwardsSpeed, rightSpeed):
        """
        attempt to move the player with the given speed
        """
        
        dPos = forwardsSpeed * self.camera.forwards + rightSpeed * self.camera.right
        
        self.camera.position[0] += dPos[0]
        self.camera.position[1] += dPos[1]
    
    def spin_player(self, dAngle):
        """
            shift the player's direction by the given amount, in degrees
        """
        self.camera.theta += dAngle[0]
        if (self.camera.theta < 0):
            self.camera.theta += 360
        elif (self.camera.theta > 360):
            self.camera.theta -= 360
        
        self.camera.phi += dAngle[1]
        if (self.camera.phi < -89):
            self.camera.phi = -89
        elif (self.camera.phi > 89):
            self.camera.phi = 89
        
        self.camera.recalculateVectors()
