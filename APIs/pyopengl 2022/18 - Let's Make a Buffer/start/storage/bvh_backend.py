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
    nodes[0]['sphere_count'] = sphere_count
    nodes[0]['contents'] = 0

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

    count = int(nodes[node_index]['sphere_count'])
    first = int(nodes[node_index]['contents'])

    for i in range(count):

        sphere_index = sphere_ids[first + i]

        #grab sphere info
        s_x = spheres[sphere_index]['x']
        s_y = spheres[sphere_index]['y']
        s_z = spheres[sphere_index]['z']
        s_r = spheres[sphere_index]['radius']

        #find new minimum
        nodes[node_index]['min_x'] = min(
            nodes[node_index]['min_x'], 
            s_x - s_r)
        nodes[node_index]['min_y'] = min(nodes[node_index]['min_y'], s_y - s_r)
        nodes[node_index]['min_z'] = min(nodes[node_index]['min_z'], s_z - s_r)
        
        #find new maximum
        nodes[node_index]['max_x'] = max(nodes[node_index]['max_x'], s_x + s_r)
        nodes[node_index]['max_y'] = max(nodes[node_index]['max_y'], s_y + s_r)
        nodes[node_index]['max_z'] = max(nodes[node_index]['max_z'], s_z + s_r)

def subdivide(nodes: np.ndarray, 
    spheres: np.ndarray, 
    sphere_ids: np.ndarray,
    node_index: int,
    nodes_used: int,
    bins: np.ndarray) -> int:

    sphere_count = int(nodes[node_index]['sphere_count'])
    if sphere_count < 2:
        return nodes_used
    
    e_x = nodes[node_index]['max_x'] - nodes[node_index]['min_x']
    e_y = nodes[node_index]['max_y'] - nodes[node_index]['min_y']
    e_z = nodes[node_index]['max_z'] - nodes[node_index]['min_z']
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

    bestPos = 0
    bestCost = 1e10
    
    sphere_count = int(nodes[node_index]['sphere_count'])
    contents = int(nodes[node_index]['contents'])
    axes = ['x', 'y', 'z']

    for i in range(sphere_count):
        sphere_index = sphere_ids[contents + i]
        testPos = spheres[sphere_index][axes[axis]]

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

    node.reset_node(dummy_left)
    node.reset_node(dummy_right)

    sphere_count = int(nodes[node_index]['sphere_count'])
    contents = int(nodes[node_index]['contents'])
    axes = ['x', 'y', 'z']

    for i in range(sphere_count):
        sphere_index = sphere_ids[contents + i]
        #get sphere info
        s_x = spheres[sphere_index]['x']
        s_y = spheres[sphere_index]['y']
        s_z = spheres[sphere_index]['z']
        s_r = spheres[sphere_index]['radius']
        s_pos = spheres[sphere_index][axes[axis]]
        
        if s_pos < split_position:
            #Grow left box
            dummy_left['min_x'] = min(dummy_left['min_x'], s_x - s_r)
            dummy_left['min_y'] = min(dummy_left['min_y'], s_y - s_r)
            dummy_left['min_z'] = min(dummy_left['min_z'], s_z - s_r)
            dummy_left['sphere_count'] = dummy_left['sphere_count'] + 1
            dummy_left['max_x'] = max(dummy_left['max_x'], s_x + s_r)
            dummy_left['max_y'] = max(dummy_left['max_y'], s_y + s_r)
            dummy_left['max_z'] = max(dummy_left['max_z'], s_z + s_r)
        else:
            #Grow right box
            dummy_right['min_x'] = min(dummy_right['min_x'], s_x - s_r)
            dummy_right['min_y'] = min(dummy_right['min_y'], s_y - s_r)
            dummy_right['min_z'] = min(dummy_right['min_z'], s_z - s_r)
            dummy_right['sphere_count'] = dummy_right['sphere_count'] + 1
            dummy_right['max_x'] = max(dummy_right['max_x'], s_x + s_r)
            dummy_right['max_y'] = max(dummy_right['max_y'], s_y + s_r)
            dummy_right['max_z'] = max(dummy_right['max_z'], s_z + s_r)
    
    l_x = dummy_left['max_x'] - dummy_left['min_x']
    l_y = dummy_left['max_y'] - dummy_left['min_y']
    l_z = dummy_left['max_z'] - dummy_left['min_z']
    l_c = int(dummy_left['sphere_count'])

    #unpack right box
    r_x = dummy_right['max_x'] - dummy_right['min_x']
    r_y = dummy_right['max_y'] - dummy_right['min_y']
    r_z = dummy_right['max_z'] - dummy_right['min_z']
    r_c = int(dummy_right['sphere_count'])

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
    
    node.reset_nodes(bins, 0, 50)
    build_bins(nodes, spheres, sphere_ids, node_index, bin_count, axis, bins)
    collect_bins(bins, bin_count)

    bestPos = 0
    bestCost = 1e10

    testPos = nodes[node_index]['min_x']
    extent = nodes[node_index]['max_x'] - testPos
    if axis == 1:
        testPos = nodes[node_index]['min_y']
        extent = nodes[node_index]['max_y'] - testPos
    elif axis == 2:
        testPos = nodes[node_index]['min_z']
        extent = nodes[node_index]['max_z'] - testPos

    scale = extent / bin_count
    for i in range(bin_count):

        left_index = i + 16
        right_index = i + 32
        #unpack left box
        l_x = bins[left_index]['max_x'] - bins[left_index]['min_x']
        l_y = bins[left_index]['max_y'] - bins[left_index]['min_y']
        l_z = bins[left_index]['max_z'] - bins[left_index]['min_z']
        l_c = int(bins[left_index]['sphere_count'])

        #unpack right box
        r_x = bins[right_index]['max_x'] - bins[right_index]['min_x']
        r_y = bins[right_index]['max_y'] - bins[right_index]['min_y']
        r_z = bins[right_index]['max_z'] - bins[right_index]['min_z']
        r_c = int(bins[right_index]['sphere_count'])

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
    #extract node info
    min_bound = nodes[node_index]['min_x']
    max_bound = nodes[node_index]['max_x']
    if axis == 1:
        min_bound = nodes[node_index]['min_y']
        max_bound = nodes[node_index]['max_y']
    elif axis == 2:
        min_bound = nodes[node_index]['min_z']
        max_bound = nodes[node_index]['max_z']
    first = int(nodes[node_index]['contents'])
    sphere_count = int(nodes[node_index]['sphere_count'])

    extent = max_bound - min_bound
    bin_size = extent / bin_count
    
    for i in range(sphere_count):
        sphere_index = sphere_ids[first + i]
        
        sphere_center = spheres[sphere_index]['x']
        if axis == 1:
            sphere_center = spheres[sphere_index]['y']
        elif axis == 2:
            sphere_center = spheres[sphere_index]['z']
        
        #unpack sphere info
        s_x = spheres[sphere_index]['x']
        s_y = spheres[sphere_index]['y']
        s_z = spheres[sphere_index]['z']
        s_r = spheres[sphere_index]['radius']
        
        sphere_offset = sphere_center - min_bound
        bin_index = max(0, min(bin_count - 1, int(sphere_offset / bin_size)))
        bins[bin_index]['min_x'] = min(bins[bin_index]['min_x'], s_x - s_r)
        bins[bin_index]['min_y'] = min(bins[bin_index]['min_y'], s_y - s_r)
        bins[bin_index]['min_z'] = min(bins[bin_index]['min_z'], s_z - s_r)
        bins[bin_index]['sphere_count'] = bins[bin_index]['sphere_count'] + 1
        bins[bin_index]['max_x'] = max(bins[bin_index]['max_x'], s_x + s_r)
        bins[bin_index]['max_y'] = max(bins[bin_index]['max_y'], s_y + s_r)
        bins[bin_index]['max_z'] = max(bins[bin_index]['max_z'], s_z + s_r)

    return bins

@njit(cache=True)
def collect_bins(bins: np.ndarray, 
    bin_count: int) -> None:

    for i in range(bin_count):

        #get bin info
        bin_index = i
        left_index = (i + 16)
        dl_index = 48
        dr_index = 49
        b_min_x = bins[bin_index]['min_x']
        b_min_y = bins[bin_index]['min_y']
        b_min_z = bins[bin_index]['min_z']
        b_count = bins[bin_index]['sphere_count']
        b_max_x = bins[bin_index]['max_x']
        b_max_y = bins[bin_index]['max_y']
        b_max_z = bins[bin_index]['max_z']
        #expand left box
        bins[dl_index]['min_x'] = min(bins[dl_index]['min_x'], b_min_x)
        bins[dl_index]['min_y'] = min(bins[dl_index]['min_y'], b_min_y)
        bins[dl_index]['min_z'] = min(bins[dl_index]['min_z'], b_min_z)
        bins[dl_index]['sphere_count'] = bins[dl_index]['sphere_count'] + b_count
        bins[dl_index]['max_x'] = max(bins[dl_index]['max_x'], b_max_x)
        bins[dl_index]['max_y'] = max(bins[dl_index]['max_y'], b_max_y)
        bins[dl_index]['max_z'] = max(bins[dl_index]['max_z'], b_max_z)
        #write it back to the list
        bins[left_index] = bins[dl_index]

        #get bin info
        bin_index = bin_count - 1 - i
        right_index = (bin_count - 1 - i + 32)
        b_min_x = bins[bin_index]['min_x']
        b_min_y = bins[bin_index]['min_y']
        b_min_z = bins[bin_index]['min_z']
        b_count = bins[bin_index]['sphere_count']
        b_max_x = bins[bin_index]['max_x']
        b_max_y = bins[bin_index]['max_y']
        b_max_z = bins[bin_index]['max_z']
        #expand right box
        bins[dr_index]['min_x'] = min(bins[dr_index]['min_x'], b_min_x)
        bins[dr_index]['min_y'] = min(bins[dr_index]['min_y'], b_min_y)
        bins[dr_index]['min_z'] = min(bins[dr_index]['min_z'], b_min_z)
        bins[dr_index]['sphere_count'] = bins[dr_index]['sphere_count'] + b_count
        bins[dr_index]['max_x'] = max(bins[dr_index]['max_x'], b_max_x)
        bins[dr_index]['max_y'] = max(bins[dr_index]['max_y'], b_max_y)
        bins[dr_index]['max_z'] = max(bins[dr_index]['max_z'], b_max_z)
        #write it back to the list
        bins[right_index] = bins[dr_index]

def object_split(nodes: np.ndarray, 
    spheres: np.ndarray, 
    sphere_ids: np.ndarray, 
    parent_index: int, axis: int, 
    nodes_used: int, split_position: float,
    bins: np.ndarray) -> int:

    sphere_count = int(nodes[parent_index]['sphere_count'])
    contents = int(nodes[parent_index]['contents'])
    axes = ['x', 'y', 'z']

    #split group into halves
    i = contents
    j = i + sphere_count - 1
    while i <= j:

        if spheres[sphere_ids[i]][axes[axis]] < split_position:
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
    nodes_used += 1
    nodes[left_child_index]['contents'] = contents
    nodes[left_child_index]['sphere_count'] = left_count
    nodes[parent_index]['contents'] = left_child_index
    
    right_child_index = nodes_used
    nodes_used += 1
    nodes[right_child_index]['contents'] = i
    nodes[right_child_index]['sphere_count'] = sphere_count - left_count

    update_bounds(nodes, spheres, sphere_ids, left_child_index)
    nodes_used = subdivide(nodes, spheres, sphere_ids, left_child_index, nodes_used, bins)
    update_bounds(nodes, spheres, sphere_ids, right_child_index)
    nodes_used = subdivide(nodes, spheres, sphere_ids, right_child_index, nodes_used, bins)

    nodes[parent_index]['sphere_count'] = 0

    return nodes_used
#endregion