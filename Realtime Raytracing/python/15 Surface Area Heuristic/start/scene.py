from config import *
import sphere
import camera
import node

class Scene:
    """
        Holds pointers to all objects in the scene
    """


    def __init__(self):
        """
            Set up scene objects.
        """
        
        sphere_count = 3000
        self.spheres = [
            sphere.Sphere(
                center = [
                    np.random.uniform(low = -95.0, high = 95.0),
                    np.random.uniform(low = -95.0, high = 95.0),
                    np.random.uniform(low = -15.0, high = 15.0)
                ],
                radius = np.random.uniform(low = 0.3, high = 2.0),
                color = [
                    np.random.uniform(low = 0.0, high = 1.0),
                    np.random.uniform(low = 0.0, high = 1.0),
                    np.random.uniform(low = 0.0, high = 1.0)
                ],
                roughness = np.random.uniform(low = 0.0, high = 1.0)
            ) for i in range(sphere_count)
        ]
        
        self.camera = camera.Camera(
            position = [0.0, 0.0, 1.0]
        )

        self.sphere_ids = [i for i in range(sphere_count)]

        self.nodes = []
        for _ in range(2 * len(self.spheres) + 1):
            self.nodes.append(node.Node())
        
        self.root_index = 0
        self.nodes_used = 0

        self.build_bvh()

        self.outDated = True
    
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
    
    def build_bvh(self):

        root: node.Node = self.nodes[self.root_index]
        root.contents = 0
        root.sphere_count = len(self.spheres)

        self.nodes_used += 1
        self.update_bounds(self.root_index)
        self.subdivide(self.root_index)
    
    def update_bounds(self, node_index):

        _node: node.Node = self.nodes[node_index]
        _node.min_corner = np.array([1e30, 1e30, 1e30], dtype=np.float32)
        _node.max_corner = np.array([-1e30, -1e30, -1e30], dtype=np.float32)
        first = _node.contents
        for i in range(_node.sphere_count):

            sphere_index = self.sphere_ids[first + i]
            _sphere = self.spheres[sphere_index]

            sphere_min = _sphere.center - _sphere.radius * np.array([1, 1, 1], dtype=np.float32)
            _node.min_corner = np.minimum(_node.min_corner, sphere_min)

            sphere_max = _sphere.center + _sphere.radius * np.array([1, 1, 1], dtype=np.float32)
            _node.max_corner = np.maximum(_node.max_corner, sphere_max)
    
    def subdivide(self, node_index):

        _node: node.Node = self.nodes[node_index]
        if _node.sphere_count < 2:
            return

        extent = _node.max_corner - _node.min_corner
        axis = 0
        if (extent[1] > extent[axis]):
            axis = 1
        if (extent[2] > extent[axis]):
            axis = 2
        split_position = _node.min_corner[axis] + 0.5 * extent[axis]

        #split group into halves
        i = _node.contents
        j = i + _node.sphere_count - 1
        while i <= j:
            if self.spheres[self.sphere_ids[i]].center[axis] < split_position:
                i += 1
            else:
                temp = self.sphere_ids[i]
                self.sphere_ids[i] = self.sphere_ids[j]
                self.sphere_ids[j] = temp
                j -= 1

        #create child nodes
        left_count = i - _node.contents
        if (left_count == 0 or left_count == _node.sphere_count):
            return
        
        left_child_index = self.nodes_used
        self.nodes_used += 1
        left_node: node.Node = self.nodes[left_child_index]
        left_node.contents = _node.contents
        left_node.sphere_count = left_count
        _node.contents = left_child_index
        
        right_child_index = self.nodes_used
        self.nodes_used += 1
        right_node: node.Node = self.nodes[right_child_index]
        right_node.contents = i
        right_node.sphere_count = _node.sphere_count - left_count

        self.update_bounds(left_child_index)
        self.subdivide(left_child_index)
        self.update_bounds(right_child_index)
        self.subdivide(right_child_index)

        _node.sphere_count = 0