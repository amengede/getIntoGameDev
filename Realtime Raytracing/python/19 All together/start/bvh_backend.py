from config import *
import node
#---- Data Oriented Design!          ----#
# In the spirit of masochism, the        #
# following functions are intended to    #
# be compiled.                           #
#----------------------------------------#

#---- BVH Building                   ----#
#region

def build_bvh(
    nodes: np.ndarray, 
    spheres: np.ndarray,
    sphere_ids: np.ndarray,
    sphere_count: int) -> int:

    #Configure root node
    #sphere count
    nodes[NODE_ATTRIBUTE_SPHERE_COUNT] = sphere_count
    nodes[NODE_ATTRIBUTE_CONTENTS] = 0

    #preallocate memory:
    # [bins -- left_bins -- right_bins -- dummy_left -- dummy_right]
    bins = node.make_nodes(50)

    update_bounds(nodes, spheres, sphere_ids, 0)
    nodes_used = subdivide(
        nodes, spheres, sphere_ids, 
        0, 1, bins)
    
    return nodes_used

def update_bounds(
    nodes: np.ndarray, 
    spheres: np.ndarray, 
    sphere_ids: np.ndarray,
    node_index: int) -> None:

    base_index = NODE_STRIDE * node_index
    count = int(nodes[base_index + NODE_ATTRIBUTE_SPHERE_COUNT])
    first = int(nodes[base_index + NODE_ATTRIBUTE_CONTENTS])

    for i in range(count):

        sphere_index = sphere_ids[first + i]

        #grab sphere info
        sphere_base_index = sphere_index * SPHERE_STRIDE
        s_x = spheres[sphere_base_index + SPHERE_ATTRIBUTE_X]
        s_y = spheres[sphere_base_index + SPHERE_ATTRIBUTE_Y]
        s_z = spheres[sphere_base_index + SPHERE_ATTRIBUTE_Z]
        s_r = spheres[sphere_base_index + SPHERE_ATTRIBUTE_RADIUS]

        #find new minimum
        nodes[base_index + NODE_ATTRIBUTE_MIN_X] = min(nodes[base_index + NODE_ATTRIBUTE_MIN_X], s_x - s_r)
        nodes[base_index + NODE_ATTRIBUTE_MIN_Y] = min(nodes[base_index + NODE_ATTRIBUTE_MIN_Y], s_y - s_r)
        nodes[base_index + NODE_ATTRIBUTE_MIN_Z] = min(nodes[base_index + NODE_ATTRIBUTE_MIN_Z], s_z - s_r)
        
        #find new maximum
        nodes[base_index + NODE_ATTRIBUTE_MAX_X] = max(nodes[base_index + NODE_ATTRIBUTE_MAX_X], s_x + s_r)
        nodes[base_index + NODE_ATTRIBUTE_MAX_Y] = max(nodes[base_index + NODE_ATTRIBUTE_MAX_Y], s_y + s_r)
        nodes[base_index + NODE_ATTRIBUTE_MAX_Z] = max(nodes[base_index + NODE_ATTRIBUTE_MAX_Z], s_z + s_r)

def subdivide(nodes: np.ndarray, 
    spheres: np.ndarray, 
    sphere_ids: np.ndarray,
    node_index: int,
    nodes_used: int,
    bins: np.ndarray) -> int:

    base_index = node_index * NODE_STRIDE
    sphere_count = int(nodes[base_index + NODE_ATTRIBUTE_SPHERE_COUNT])
    if sphere_count < 2:
        return nodes_used
    
    e_x = nodes[base_index + NODE_ATTRIBUTE_MAX_X] - nodes[base_index + NODE_ATTRIBUTE_MIN_X]
    e_y = nodes[base_index + NODE_ATTRIBUTE_MAX_Y] - nodes[base_index + NODE_ATTRIBUTE_MIN_Y]
    e_z = nodes[base_index + NODE_ATTRIBUTE_MAX_Z] - nodes[base_index + NODE_ATTRIBUTE_MIN_Z]
    e = e_x
    bestAxis = 0
    if e_y > e:
        bestAxis = 1
        e = e_y
    if e_z > e:
        bestAxis = 2
        e = e_z
    
    bin_count = 16
    """
    if sphere_count >= bin_count:
        pos, cost = determine_best_split_bin(
            nodes, spheres, sphere_ids, 
            node_index, bestAxis, bin_count,
            bins, left_bins, right_bins,
            dummy_left, dummy_right)
    else:
        pos, cost = determine_best_split_full(
            nodes, spheres, sphere_ids, 
            node_index, bestAxis, dummy_left, dummy_right)
    """
    pos, cost = determine_best_split_bin(
        nodes, spheres, sphere_ids, 
        node_index, bestAxis, bin_count,
        bins)
    
    node_cost = sphere_count * (e_x * e_y + e_y * e_z + e_x * e_z)
    
    if cost >= node_cost:
        return nodes_used

    return object_split(
        nodes, spheres, sphere_ids, node_index, bestAxis, nodes_used, pos,
        bins)

@njit(cache=True)
def determine_best_split_full(nodes: np.ndarray, 
    spheres: np.ndarray, 
    sphere_ids: np.ndarray,
    node_index: int, axis: int,
    dummy_left: np.ndarray,
    dummy_right: np.ndarray) -> tuple[float, float]:

    base_index = NODE_STRIDE * node_index

    bestPos = 0
    bestCost = 1e10
    
    sphere_count = int(nodes[base_index + NODE_ATTRIBUTE_SPHERE_COUNT])
    contents = int(nodes[base_index + NODE_ATTRIBUTE_CONTENTS])

    for i in range(sphere_count):
        sphere_index = sphere_ids[contents + i] * SPHERE_STRIDE
        testPos = spheres[sphere_index + axis]

        cost = evaluate_sah(nodes, spheres, sphere_ids, node_index, axis, testPos, dummy_left, dummy_right)

        if cost < bestCost:
            bestPos = testPos
            bestCost = cost

    return (bestPos, bestCost)

@njit(cache=True)
def evaluate_sah(nodes: np.ndarray,
    spheres: np.ndarray,
    sphere_ids: np.ndarray,
    node_index: int, axis: int, split_position: float,
    dummy_left: np.ndarray,
    dummy_right: np.ndarray) -> float:

    base_index = node_index * NODE_STRIDE
    node.reset_node(dummy_left)
    node.reset_node(dummy_right)

    sphere_count = int(nodes[base_index + NODE_ATTRIBUTE_SPHERE_COUNT])
    contents = int(nodes[base_index + NODE_ATTRIBUTE_CONTENTS])

    for i in range(sphere_count):
        sphere_index = sphere_ids[contents + i] * SPHERE_STRIDE
        #get sphere info
        s_x = spheres[sphere_index + SPHERE_ATTRIBUTE_X]
        s_y = spheres[sphere_index + SPHERE_ATTRIBUTE_Y]
        s_z = spheres[sphere_index + SPHERE_ATTRIBUTE_Z]
        s_r = spheres[sphere_index + SPHERE_ATTRIBUTE_RADIUS]
        s_pos = spheres[sphere_index + axis]
        
        if s_pos < split_position:
            #Grow left box
            dummy_left[NODE_ATTRIBUTE_MIN_X] = min(dummy_left[NODE_ATTRIBUTE_MIN_X], s_x - s_r)
            dummy_left[NODE_ATTRIBUTE_MIN_Y] = min(dummy_left[NODE_ATTRIBUTE_MIN_Y], s_y - s_r)
            dummy_left[NODE_ATTRIBUTE_MIN_Z] = min(dummy_left[NODE_ATTRIBUTE_MIN_Z], s_z - s_r)
            dummy_left[NODE_ATTRIBUTE_SPHERE_COUNT] = dummy_left[NODE_ATTRIBUTE_SPHERE_COUNT] + 1
            dummy_left[NODE_ATTRIBUTE_MAX_X] = max(dummy_left[NODE_ATTRIBUTE_MAX_X], s_x + s_r)
            dummy_left[NODE_ATTRIBUTE_MAX_Y] = max(dummy_left[NODE_ATTRIBUTE_MAX_Y], s_y + s_r)
            dummy_left[NODE_ATTRIBUTE_MAX_Z] = max(dummy_left[NODE_ATTRIBUTE_MAX_Z], s_z + s_r)
        else:
            #Grow right box
            dummy_right[NODE_ATTRIBUTE_MIN_X] = min(dummy_right[NODE_ATTRIBUTE_MIN_X], s_x - s_r)
            dummy_right[NODE_ATTRIBUTE_MIN_Y] = min(dummy_right[NODE_ATTRIBUTE_MIN_Y], s_y - s_r)
            dummy_right[NODE_ATTRIBUTE_MIN_Z] = min(dummy_right[NODE_ATTRIBUTE_MIN_Z], s_z - s_r)
            dummy_right[NODE_ATTRIBUTE_SPHERE_COUNT] = dummy_right[NODE_ATTRIBUTE_SPHERE_COUNT] + 1
            dummy_right[NODE_ATTRIBUTE_MAX_X] = max(dummy_right[NODE_ATTRIBUTE_MAX_X], s_x + s_r)
            dummy_right[NODE_ATTRIBUTE_MAX_Y] = max(dummy_right[NODE_ATTRIBUTE_MAX_Y], s_y + s_r)
            dummy_right[NODE_ATTRIBUTE_MAX_Z] = max(dummy_right[NODE_ATTRIBUTE_MAX_Z], s_z + s_r)
    
    l_x = dummy_left[NODE_ATTRIBUTE_MAX_X] - dummy_left[NODE_ATTRIBUTE_MIN_X]
    l_y = dummy_left[NODE_ATTRIBUTE_MAX_Y] - dummy_left[NODE_ATTRIBUTE_MIN_Y]
    l_z = dummy_left[NODE_ATTRIBUTE_MAX_Z] - dummy_left[NODE_ATTRIBUTE_MIN_Z]
    l_c = int(dummy_left[NODE_ATTRIBUTE_SPHERE_COUNT])

    #unpack right box
    r_x = dummy_right[NODE_ATTRIBUTE_MAX_X] - dummy_right[NODE_ATTRIBUTE_MIN_X]
    r_y = dummy_right[NODE_ATTRIBUTE_MAX_Y] - dummy_right[NODE_ATTRIBUTE_MIN_Y]
    r_z = dummy_right[NODE_ATTRIBUTE_MAX_Z] - dummy_right[NODE_ATTRIBUTE_MIN_Z]
    r_c = int(dummy_right[NODE_ATTRIBUTE_SPHERE_COUNT])

    cost = l_c * (l_x * l_y + l_y * l_z + l_x * l_z) \
        + r_c * (r_x * r_y + r_y * r_z + r_x * r_z)

    if cost < 0:
        cost = 1e30
    return cost

@njit(cache=True)
def determine_best_split_bin(nodes: np.ndarray, 
    spheres: np.ndarray, 
    sphere_ids: np.ndarray,
    node_index: int, axis: int, bin_count: int,
    bins: np.ndarray) -> tuple[float, float]:

    base_index = node_index * NODE_STRIDE
    
    node.reset_nodes(bins, 0, 50)
    build_bins(nodes, spheres, sphere_ids, node_index, bin_count, axis, bins)
    collect_bins(bins, bin_count)

    bestPos = 0
    bestCost = 1e10
    testPos = nodes[base_index + axis]
    extent = nodes[base_index + NODE_ATTRIBUTE_MAX_X + axis] - testPos
    scale = extent / bin_count
    for i in range(bin_count):

        left_index = NODE_STRIDE * (i + 16)
        right_index = NODE_STRIDE * (i + 32)
        #unpack left box
        l_x = bins[left_index + NODE_ATTRIBUTE_MAX_X] - bins[left_index + NODE_ATTRIBUTE_MIN_X]
        l_y = bins[left_index + NODE_ATTRIBUTE_MAX_Y] - bins[left_index + NODE_ATTRIBUTE_MIN_Y]
        l_z = bins[left_index + NODE_ATTRIBUTE_MAX_Z] - bins[left_index + NODE_ATTRIBUTE_MIN_Z]
        l_c = int(bins[left_index + NODE_ATTRIBUTE_SPHERE_COUNT])

        #unpack right box
        r_x = bins[right_index + NODE_ATTRIBUTE_MAX_X] - bins[right_index + NODE_ATTRIBUTE_MIN_X]
        r_y = bins[right_index + NODE_ATTRIBUTE_MAX_Y] - bins[right_index + NODE_ATTRIBUTE_MIN_Y]
        r_z = bins[right_index + NODE_ATTRIBUTE_MAX_Z] - bins[right_index + NODE_ATTRIBUTE_MIN_Z]
        r_c = int(bins[right_index + NODE_ATTRIBUTE_SPHERE_COUNT])

        cost = l_c * (l_x * l_y + l_y * l_z + l_x * l_z) \
            + r_c * (r_x * r_y + r_y * r_z + r_x * r_z)
        if cost < bestCost:
            bestPos = testPos + (i + 1) * scale
            bestCost = cost

    return (bestPos, bestCost)

@njit(cache=True)
def build_bins(nodes: np.ndarray, 
    spheres: np.ndarray, 
    sphere_ids: np.ndarray, node_index: int, bin_count: int, axis: int, bins: np.ndarray) -> np.ndarray:

    node.reset_nodes(bins, 0, bin_count)
    base_index = NODE_STRIDE * node_index
    #extract node info
    min_bound = nodes[base_index + NODE_ATTRIBUTE_MIN_X + axis]
    max_bound = nodes[base_index + NODE_ATTRIBUTE_MAX_X + axis]
    first = int(nodes[base_index + NODE_ATTRIBUTE_CONTENTS])
    sphere_count = int(nodes[base_index + NODE_ATTRIBUTE_SPHERE_COUNT])

    extent = max_bound - min_bound
    bin_size = extent / bin_count
    for i in range(sphere_count):
        sphere_index = sphere_ids[first + i] * SPHERE_STRIDE
        
        sphere_center = spheres[sphere_index + axis]
        #unpack sphere info
        s_x = spheres[sphere_index + SPHERE_ATTRIBUTE_X]
        s_y = spheres[sphere_index + SPHERE_ATTRIBUTE_Y]
        s_z = spheres[sphere_index + SPHERE_ATTRIBUTE_Z]
        s_r = spheres[sphere_index + SPHERE_ATTRIBUTE_RADIUS]
        
        sphere_offset = sphere_center - min_bound
        bin_index = NODE_STRIDE * max(0, min(bin_count - 1, int(sphere_offset / bin_size)))
        bins[bin_index + NODE_ATTRIBUTE_MIN_X] = min(bins[bin_index + NODE_ATTRIBUTE_MIN_X], s_x - s_r)
        bins[bin_index + NODE_ATTRIBUTE_MIN_Y] = min(bins[bin_index + NODE_ATTRIBUTE_MIN_Y], s_y - s_r)
        bins[bin_index + NODE_ATTRIBUTE_MIN_Z] = min(bins[bin_index + NODE_ATTRIBUTE_MIN_Z], s_z - s_r)
        bins[bin_index + NODE_ATTRIBUTE_SPHERE_COUNT] = bins[bin_index + NODE_ATTRIBUTE_SPHERE_COUNT] + 1
        bins[bin_index + NODE_ATTRIBUTE_MAX_X] = max(bins[bin_index + NODE_ATTRIBUTE_MAX_X], s_x + s_r)
        bins[bin_index + NODE_ATTRIBUTE_MAX_Y] = max(bins[bin_index + NODE_ATTRIBUTE_MAX_Y], s_y + s_r)
        bins[bin_index + NODE_ATTRIBUTE_MAX_Z] = max(bins[bin_index + NODE_ATTRIBUTE_MAX_Z], s_z + s_r)

    return bins

@njit(cache=True)
def collect_bins(bins: np.ndarray, 
    bin_count: int) -> None:

    for i in range(bin_count):

        #get bin info
        bin_index = i * NODE_STRIDE
        left_index = (i + 16) * NODE_STRIDE
        dl_index = 48 * NODE_STRIDE
        dr_index = 49 * NODE_STRIDE
        b_min_x = bins[bin_index + NODE_ATTRIBUTE_MIN_X]
        b_min_y = bins[bin_index + NODE_ATTRIBUTE_MIN_Y]
        b_min_z = bins[bin_index + NODE_ATTRIBUTE_MIN_Z]
        b_count = bins[bin_index + NODE_ATTRIBUTE_SPHERE_COUNT]
        b_max_x = bins[bin_index + NODE_ATTRIBUTE_MAX_X]
        b_max_y = bins[bin_index + NODE_ATTRIBUTE_MAX_Y]
        b_max_z = bins[bin_index + NODE_ATTRIBUTE_MAX_Z]
        #expand left box
        bins[dl_index + NODE_ATTRIBUTE_MIN_X] = min(bins[dl_index + NODE_ATTRIBUTE_MIN_X], b_min_x)
        bins[dl_index + NODE_ATTRIBUTE_MIN_Y] = min(bins[dl_index + NODE_ATTRIBUTE_MIN_Y], b_min_y)
        bins[dl_index + NODE_ATTRIBUTE_MIN_Z] = min(bins[dl_index + NODE_ATTRIBUTE_MIN_Z], b_min_z)
        bins[dl_index + NODE_ATTRIBUTE_SPHERE_COUNT] = bins[dl_index + NODE_ATTRIBUTE_SPHERE_COUNT] + b_count
        bins[dl_index + NODE_ATTRIBUTE_MAX_X] = max(bins[dl_index + NODE_ATTRIBUTE_MAX_X], b_max_x)
        bins[dl_index + NODE_ATTRIBUTE_MAX_Y] = max(bins[dl_index + NODE_ATTRIBUTE_MAX_Y], b_max_y)
        bins[dl_index + NODE_ATTRIBUTE_MAX_Z] = max(bins[dl_index + NODE_ATTRIBUTE_MAX_Z], b_max_z)
        #write it back to the list
        for attribute in range(7):
            bins[left_index + attribute] = bins[dl_index + attribute]

        #get bin info
        bin_index = 8 * (bin_count - 1 - i)
        right_index = (bin_count - 1 - i + 32) * NODE_STRIDE
        b_min_x = bins[bin_index + NODE_ATTRIBUTE_MIN_X]
        b_min_y = bins[bin_index + NODE_ATTRIBUTE_MIN_Y]
        b_min_z = bins[bin_index + NODE_ATTRIBUTE_MIN_Z]
        b_count = bins[bin_index + NODE_ATTRIBUTE_SPHERE_COUNT]
        b_max_x = bins[bin_index + NODE_ATTRIBUTE_MAX_X]
        b_max_y = bins[bin_index + NODE_ATTRIBUTE_MAX_Y]
        b_max_z = bins[bin_index + NODE_ATTRIBUTE_MAX_Z]
        #expand right box
        bins[dr_index + NODE_ATTRIBUTE_MIN_X] = min(bins[dr_index + NODE_ATTRIBUTE_MIN_X], b_min_x)
        bins[dr_index + NODE_ATTRIBUTE_MIN_Y] = min(bins[dr_index + NODE_ATTRIBUTE_MIN_Y], b_min_y)
        bins[dr_index + NODE_ATTRIBUTE_MIN_Z] = min(bins[dr_index + NODE_ATTRIBUTE_MIN_Z], b_min_z)
        bins[dr_index + NODE_ATTRIBUTE_SPHERE_COUNT] = bins[dr_index + NODE_ATTRIBUTE_SPHERE_COUNT] + b_count
        bins[dr_index + NODE_ATTRIBUTE_MAX_X] = max(bins[dr_index + NODE_ATTRIBUTE_MAX_X], b_max_x)
        bins[dr_index + NODE_ATTRIBUTE_MAX_Y] = max(bins[dr_index + NODE_ATTRIBUTE_MAX_Y], b_max_y)
        bins[dr_index + NODE_ATTRIBUTE_MAX_Z] = max(bins[dr_index + NODE_ATTRIBUTE_MAX_Z], b_max_z)
        #write it back to the list
        for attribute in range(7):
            bins[right_index + attribute] = bins[dr_index + attribute]

def object_split(nodes: np.ndarray, 
    spheres: np.ndarray, 
    sphere_ids: np.ndarray, 
    parent_index: int, axis: int, 
    nodes_used: int, split_position: float,
    bins: np.ndarray) -> int:

    base_index = NODE_STRIDE * parent_index
    sphere_count = int(nodes[base_index + NODE_ATTRIBUTE_SPHERE_COUNT])
    contents = int(nodes[base_index + NODE_ATTRIBUTE_CONTENTS])

    #split group into halves
    i = contents
    j = i + sphere_count - 1
    while i <= j:
        if spheres[SPHERE_STRIDE * sphere_ids[i] + axis] < split_position:
            i += 1
        else:
            temp = sphere_ids[i]
            sphere_ids[i] = sphere_ids[j]
            sphere_ids[j] = temp
            j -= 1

    #create child nodes
    left_count = i - contents
    if (left_count == 0 or left_count == sphere_count):
        return nodes_used
    
    left_child_index = nodes_used
    left_base_index = left_child_index * NODE_STRIDE
    nodes_used += 1
    nodes[left_base_index + NODE_ATTRIBUTE_CONTENTS] = contents
    nodes[left_base_index + NODE_ATTRIBUTE_SPHERE_COUNT] = left_count
    nodes[base_index + NODE_ATTRIBUTE_CONTENTS] = left_child_index
    
    right_child_index = nodes_used
    nodes_used += 1
    right_base_index = right_child_index * NODE_STRIDE
    nodes[right_base_index + NODE_ATTRIBUTE_CONTENTS] = i
    nodes[right_base_index + NODE_ATTRIBUTE_SPHERE_COUNT] = sphere_count - left_count

    update_bounds(nodes, spheres, sphere_ids, left_child_index)
    nodes_used = subdivide(nodes, spheres, sphere_ids, left_child_index, nodes_used, bins)
    update_bounds(nodes, spheres, sphere_ids, right_child_index)
    nodes_used = subdivide(nodes, spheres, sphere_ids, right_child_index, nodes_used, bins)

    nodes[base_index + NODE_ATTRIBUTE_SPHERE_COUNT] = 0

    return nodes_used
#endregion