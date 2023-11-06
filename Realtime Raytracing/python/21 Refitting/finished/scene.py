from config import *
import sphere
import camera
import node
import bvh_backend
import materials

class Scene:
    """
        Holds pointers to all objects in the scene
    """


    def __init__(self):
        """
            Set up scene objects.
        """
        
        self.rebuild_count = 0
        material_count = 16
        self.materials = materials.make_materials(material_count)
        self.sphere_count = 3000
        self.spheres = sphere.make_spheres(self.sphere_count, material_count)
        
        self.camera = camera.Camera(
            position = [0.0, 0.0, 1.0]
        )

        self.sphere_ids = np.arange(self.sphere_count, dtype=np.int32)

        self.nodes = node.make_nodes(2 * self.sphere_count + 1)

        start = time.time()
        self.nodes_used = bvh_backend.build_bvh(
            self.nodes, self.spheres, self.sphere_ids, self.sphere_count)
        finish = time.time()
        print(f"BVH build took {(finish - start) * 1000} ms.")

        """
        for i in range(self.nodes_used):
            node.print_node(self.nodes[i], i)
        """

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
    
    def update(self, dt: float) -> None:
        """
            Update everything in the scene
        """

        self.outDated = True
        sphere.update_spheres(self.spheres, dt)

        if self.rebuild_count == 16:
            self.nodes_used = bvh_backend.build_bvh(
                self.nodes, self.spheres, 
                self.sphere_ids, self.sphere_count)
            self.rebuild_count = 0
        else:
            bvh_backend.refit_bvh(self.nodes, self.spheres, self.sphere_ids, self.nodes_used)
            self.rebuild_count += 1
