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
    nodes[3] = sphere_count
    nodes[7] = 0

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

    base_index = 8 * node_index
    count = int(nodes[base_index + 3])
    first = int(nodes[base_index + 7])

    for i in range(count):

        sphere_index = sphere_ids[first + i]

        #grab sphere info
        sphere_base_index = sphere_index * 8
        s_x = spheres[sphere_base_index]
        s_y = spheres[sphere_base_index + 1]
        s_z = spheres[sphere_base_index + 2]
        s_r = spheres[sphere_base_index + 3]

        #find new minimum
        nodes[base_index]     = min(nodes[base_index],     s_x - s_r)
        nodes[base_index + 1] = min(nodes[base_index + 1], s_y - s_r)
        nodes[base_index + 2] = min(nodes[base_index + 2], s_z - s_r)
        
        #find new maximum
        nodes[base_index + 4] = max(nodes[base_index + 4], s_x + s_r)
        nodes[base_index + 5] = max(nodes[base_index + 5], s_y + s_r)
        nodes[base_index + 6] = max(nodes[base_index + 6], s_z + s_r)

def subdivide(nodes: np.ndarray, 
    spheres: np.ndarray, 
    sphere_ids: np.ndarray,
    node_index: int,
    nodes_used: int,
    bins: np.ndarray) -> int:

    base_index = node_index * 8
    sphere_count = int(nodes[base_index + 3])
    if sphere_count < 2:
        return nodes_used
    
    e_x = nodes[base_index + 4] - nodes[base_index]
    e_y = nodes[base_index + 5] - nodes[base_index + 1]
    e_z = nodes[base_index + 6] - nodes[base_index + 2]
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

    base_index = 8 * node_index

    bestPos = 0
    bestCost = 1e10
    
    sphere_count = int(nodes[base_index + 3])
    contents = int(nodes[base_index + 7])

    for i in range(sphere_count):
        sphere_index = sphere_ids[contents + i] * 8
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

    base_index = node_index * 8
    node.reset_node(dummy_left)
    node.reset_node(dummy_right)

    sphere_count = int(nodes[base_index + 3])
    contents = int(nodes[base_index + 7])

    for i in range(sphere_count):
        sphere_index = sphere_ids[contents + i] * 8
        #get sphere info
        s_x = spheres[sphere_index]
        s_y = spheres[sphere_index + 1]
        s_z = spheres[sphere_index + 2]
        s_r = spheres[sphere_index + 3]
        s_pos = spheres[sphere_index + axis]
        
        if s_pos < split_position:
            #Grow left box
            dummy_left[0] = min(dummy_left[0], s_x - s_r)
            dummy_left[1] = min(dummy_left[1], s_y - s_r)
            dummy_left[2] = min(dummy_left[2], s_z - s_r)
            dummy_left[3] = dummy_left[3] + 1
            dummy_left[4] = max(dummy_left[4], s_x + s_r)
            dummy_left[5] = max(dummy_left[5], s_y + s_r)
            dummy_left[6] = max(dummy_left[6], s_z + s_r)
        else:
            #Grow right box
            dummy_right[0] = min(dummy_right[0], s_x - s_r)
            dummy_right[1] = min(dummy_right[1], s_y - s_r)
            dummy_right[2] = min(dummy_right[2], s_z - s_r)
            dummy_right[3] = dummy_right[3] + 1
            dummy_right[4] = max(dummy_right[4], s_x + s_r)
            dummy_right[5] = max(dummy_right[5], s_y + s_r)
            dummy_right[6] = max(dummy_right[6], s_z + s_r)
    
    l_x = dummy_left[4] - dummy_left[0]
    l_y = dummy_left[5] - dummy_left[1]
    l_z = dummy_left[6] - dummy_left[2]
    l_c = int(dummy_left[3])

    #unpack right box
    r_x = dummy_right[4] - dummy_right[0]
    r_y = dummy_right[5] - dummy_right[1]
    r_z = dummy_right[6] - dummy_right[2]
    r_c = int(dummy_right[3])

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

    base_index = node_index * 8
    
    node.reset_nodes(bins, 0, 50)
    build_bins(nodes, spheres, sphere_ids, node_index, bin_count, axis, bins)
    collect_bins(bins, bin_count)

    bestPos = 0
    bestCost = 1e10
    testPos = nodes[base_index + axis]
    extent = nodes[base_index + 4 + axis] - testPos
    scale = extent / bin_count
    for i in range(bin_count):

        left_index = 8 * (i + 16)
        right_index = 8 * (i + 32)
        #unpack left box
        l_x = bins[left_index + 4] - bins[left_index]
        l_y = bins[left_index + 5] - bins[left_index + 1]
        l_z = bins[left_index + 6] - bins[left_index + 2]
        l_c = int(bins[left_index + 3])

        #unpack right box
        r_x = bins[right_index + 4] - bins[right_index]
        r_y = bins[right_index + 5] - bins[right_index + 1]
        r_z = bins[right_index + 6] - bins[right_index + 2]
        r_c = int(bins[right_index + 3])

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
    base_index = 8 * node_index
    #extract node info
    min_bound = nodes[base_index + axis]
    max_bound = nodes[base_index + 4 + axis]
    first = int(nodes[base_index + 7])
    sphere_count = int(nodes[base_index + 3])

    extent = max_bound - min_bound
    bin_size = extent / bin_count
    for i in range(sphere_count):
        sphere_index = sphere_ids[first + i] * 8
        
        sphere_center = spheres[sphere_index + axis]
        #unpack sphere info
        s_x = spheres[sphere_index]
        s_y = spheres[sphere_index + 1]
        s_z = spheres[sphere_index + 2]
        s_r = spheres[sphere_index + 3]
        
        sphere_offset = sphere_center - min_bound
        bin_index = 8 *max(0, min(bin_count - 1, int(sphere_offset / bin_size)))
        bins[bin_index]     = min(bins[bin_index],     s_x - s_r)
        bins[bin_index + 1] = min(bins[bin_index + 1], s_y - s_r)
        bins[bin_index + 2] = min(bins[bin_index + 2], s_z - s_r)
        bins[bin_index + 3] = bins[bin_index + 3] + 1
        bins[bin_index + 4] = max(bins[bin_index + 4], s_x + s_r)
        bins[bin_index + 5] = max(bins[bin_index + 5], s_y + s_r)
        bins[bin_index + 6] = max(bins[bin_index + 6], s_z + s_r)

    return bins

@njit(cache=True)
def collect_bins(bins: np.ndarray, 
    bin_count: int) -> None:

    for i in range(bin_count):

        #get bin info
        bin_index = i * 8
        left_index = (i + 16) * 8
        dl_index = 48 * 8
        dr_index = 49 * 8
        b_min_x = bins[bin_index]
        b_min_y = bins[bin_index + 1]
        b_min_z = bins[bin_index + 2]
        b_count = bins[bin_index + 3]
        b_max_x = bins[bin_index + 4]
        b_max_y = bins[bin_index + 5]
        b_max_z = bins[bin_index + 6]
        #expand left box
        bins[dl_index]     = min(bins[dl_index], b_min_x)
        bins[dl_index + 1] = min(bins[dl_index + 1], b_min_y)
        bins[dl_index + 2] = min(bins[dl_index + 2], b_min_z)
        bins[dl_index + 3] = bins[dl_index + 3] + b_count
        bins[dl_index + 4] = max(bins[dl_index + 4], b_max_x)
        bins[dl_index + 5] = max(bins[dl_index + 5], b_max_y)
        bins[dl_index + 6] = max(bins[dl_index + 6], b_max_z)
        #write it back to the list
        for attribute in range(7):
            bins[left_index + attribute] = bins[dl_index + attribute]

        #get bin info
        bin_index = 8 * (bin_count - 1 - i)
        right_index = (bin_count - 1 - i + 32) * 8
        b_min_x = bins[bin_index]
        b_min_y = bins[bin_index + 1]
        b_min_z = bins[bin_index + 2]
        b_count = bins[bin_index + 3]
        b_max_x = bins[bin_index + 4]
        b_max_y = bins[bin_index + 5]
        b_max_z = bins[bin_index + 6]
        #expand right box
        bins[dr_index]     = min(bins[dr_index], b_min_x)
        bins[dr_index + 1] = min(bins[dr_index + 1], b_min_y)
        bins[dr_index + 2] = min(bins[dr_index + 2], b_min_z)
        bins[dr_index + 3] = bins[dr_index + 3] + b_count
        bins[dr_index + 4] = max(bins[dr_index + 4], b_max_x)
        bins[dr_index + 5] = max(bins[dr_index + 5], b_max_y)
        bins[dr_index + 6] = max(bins[dr_index + 6], b_max_z)
        #write it back to the list
        for attribute in range(7):
            bins[right_index + attribute] = bins[dr_index + attribute]

def object_split(nodes: np.ndarray, 
    spheres: np.ndarray, 
    sphere_ids: np.ndarray, 
    parent_index: int, axis: int, 
    nodes_used: int, split_position: float,
    bins: np.ndarray) -> int:

    base_index = 8 * parent_index
    sphere_count = int(nodes[base_index + 3])
    contents = int(nodes[base_index + 7])

    #split group into halves
    i = contents
    j = i + sphere_count - 1
    while i <= j:
        if spheres[8 * sphere_ids[i] + axis] < split_position:
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
    left_base_index = left_child_index * 8
    nodes_used += 1
    nodes[left_base_index + 7] = contents
    nodes[left_base_index + 3] = left_count
    nodes[base_index + 7] = left_child_index
    
    right_child_index = nodes_used
    nodes_used += 1
    right_base_index = right_child_index * 8
    nodes[right_base_index + 7] = i
    nodes[right_base_index + 3] = sphere_count - left_count

    update_bounds(nodes, spheres, sphere_ids, left_child_index)
    nodes_used = subdivide(nodes, spheres, sphere_ids, left_child_index, nodes_used, bins)
    update_bounds(nodes, spheres, sphere_ids, right_child_index)
    nodes_used = subdivide(nodes, spheres, sphere_ids, right_child_index, nodes_used, bins)

    nodes[base_index + 3] = 0

    return nodes_used
#endregion