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

        self.sphere_ids = np.array([i for i in range(sphere_count)], dtype = np.int32)

        self.nodes: list[node.Node] = [node.Node() for _ in range(2 * sphere_count + 1)]
        
        self.root_index = 0
        self.nodes_used = 0

        start = time.time()
        self.build_bvh()
        finish = time.time()
        print(f"BVH build took {(finish - start) * 1000} ms.")

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
    
    def update_bounds(self, node_index: int) -> None:

        _node: node.Node = self.nodes[node_index]
        first = _node.contents

        for i in range(_node.sphere_count):

            sphere_index = self.sphere_ids[first + i]
            _sphere = self.spheres[sphere_index]

            _node.grow(_sphere)
    
    def subdivide(self, node_index: int) -> None:

        _node: node.Node = self.nodes[node_index]
        if _node.sphere_count < 2:
            return
        
        bin_count = 64
        if _node.sphere_count < bin_count:
            axis, split_position, cost = self.determine_best_split_full(node_index)
        else:
            axis, split_position, cost = self.determine_best_split_bin(node_index, bin_count)
        
        if cost >= _node.get_cost():
            return

        self.object_split(node_index, axis, split_position)
    
    def determine_best_split_full(self, node_index: int) -> tuple[int, float, float]:

        _node: node.Node = self.nodes[node_index]

        extent = _node.max_corner - _node.min_corner
        bestAxis = 0
        if extent[1] > extent[bestAxis]:
            bestAxis = 1
        if extent[2] > extent[bestAxis]:
            bestAxis = 2
        bestPos = 0
        bestCost = 1e30
        first = _node.contents
        for i in range(_node.sphere_count):
            sphere_index = self.sphere_ids[first + i]
            _sphere = self.spheres[sphere_index]
            testPos = _sphere.center[bestAxis]
            cost = self.evaluate_sah(node_index, bestAxis, testPos)
            if cost < bestCost:
                bestPos = testPos
                bestCost = cost

        return bestAxis, bestPos, bestCost

    def evaluate_sah(self, node_index: int, axis: int, split_position: float) -> float:

        _node = self.nodes[node_index]
        dummy_left = node.Node()
        dummy_right = node.Node()

        first = _node.contents
        for i in range(_node.sphere_count):
            sphere_index: int = self.sphere_ids[first + i]
            _sphere = self.spheres[sphere_index]
            if _sphere.center[axis] < split_position:
                dummy_left.sphere_count += 1
                dummy_left.grow(_sphere)
            else:
                dummy_right.sphere_count += 1
                dummy_right.grow(_sphere)
        
        cost = dummy_left.get_cost() + dummy_right.get_cost()
        if cost < 0:
            cost = 1e30
        return cost
    
    def determine_best_split_bin(self, node_index: int, bin_count: int) -> tuple[int, float, float]:

        _node: node.Node = self.nodes[node_index]

        extent = _node.max_corner - _node.min_corner
        bestAxis = 0
        if extent[1] > extent[bestAxis]:
            bestAxis = 1
        if extent[2] > extent[bestAxis]:
            bestAxis = 2
        
        bins = self.build_bins(node_index, bin_count, bestAxis)
        left_bins, right_bins = self.collect_bins(bins)

        bestPos = 0
        bestCost = 1e30
        testPos = _node.min_corner[bestAxis]
        scale = extent[bestAxis] / bin_count
        for i in range(bin_count):

            cost = left_bins[i].get_cost() + right_bins[i].get_cost()
            if cost < bestCost:
                bestPos = testPos + (i + 1) * scale
                bestCost = cost

        return bestAxis, bestPos, bestCost

    def build_bins(self, node_index: int, bin_count: int, axis: int) -> list[node.Node]:

        bins = [node.Node() for _ in range(bin_count)]
        _node: node.Node = self.nodes[node_index]
        first = _node.contents

        extent = _node.max_corner[axis] - _node.min_corner[axis]
        bin_size = extent / bin_count
        for i in range(_node.sphere_count):
            sphere_index: int = self.sphere_ids[first + i]
            _sphere = self.spheres[sphere_index]
            
            sphere_offset = _sphere.center[axis] - _node.min_corner[axis]
            bin_index = max(0, min(bin_count - 1, int(sphere_offset / bin_size)))
            bins[bin_index].grow(_sphere)
            bins[bin_index].sphere_count += 1

        return bins
    
    def collect_bins(self, bins: list[node.Node]) -> tuple[list[node.Node], list[node.Node]]:

        bin_count = len(bins)
        left_bins = [node.Node() for _ in range(bin_count)]
        right_bins = [node.Node() for _ in range(bin_count)]
        
        dummy_left = node.Node()
        dummy_right = node.Node()
        for i in range(bin_count):

            bin_index = i
            bin = bins[bin_index]
            dummy_left.sphere_count += bin.sphere_count
            dummy_left.min_corner = np.minimum(dummy_left.min_corner, bin.min_corner)
            dummy_left.max_corner = np.maximum(dummy_left.max_corner, bin.max_corner)
            left_bins[bin_index].sphere_count = dummy_left.sphere_count
            left_bins[bin_index].min_corner = dummy_left.min_corner.copy()
            left_bins[bin_index].max_corner = dummy_left.max_corner.copy()

            bin_index = bin_count - 1 - i
            bin = bins[bin_index]
            dummy_right.sphere_count += bin.sphere_count
            dummy_right.min_corner = np.minimum(dummy_right.min_corner, bin.min_corner)
            dummy_right.max_corner = np.maximum(dummy_right.max_corner, bin.max_corner)
            right_bins[bin_index].sphere_count = dummy_right.sphere_count
            right_bins[bin_index].min_corner = dummy_right.min_corner.copy()
            right_bins[bin_index].max_corner = dummy_right.max_corner.copy()

        return (left_bins, right_bins)

    def object_split(self, parent_index: int, axis: int, split_position: float) -> None:

        _node: node.Node = self.nodes[parent_index]

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