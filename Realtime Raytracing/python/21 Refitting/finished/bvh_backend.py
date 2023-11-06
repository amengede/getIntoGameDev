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

    _node = nodes[node_index]
    count = int(_node['sphere_count'])
    first = int(_node['contents'])

    for i in range(count):

        sphere_index = sphere_ids[first + i]

        #grab sphere info
        sphere = spheres[sphere_index]
        s_x = sphere['x']
        s_y = sphere['y']
        s_z = sphere['z']
        s_r = sphere['radius']

        #find new minimum
        nodes[node_index]['min_x'] = min(nodes[node_index]['min_x'], s_x - s_r)
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
    
    if sphere_count >= bin_count:
        pos, cost = determine_best_split_bin(
            nodes, spheres, sphere_ids, 
            node_index, bestAxis, bin_count,
            bins)
    else:
        pos, cost = determine_best_split_full(
            nodes, spheres, sphere_ids, 
            node_index, bestAxis, bins)
    """
    pos, cost = determine_best_split_bin(
        nodes, spheres, sphere_ids, 
        node_index, bestAxis, bin_count,
        bins)
    """
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
    bins: np.ndarray) -> tuple[float, float]:

    _node = nodes[node_index]

    bestPos = 0
    bestCost = 1e10
    
    sphere_count = int(_node['sphere_count'])
    contents = int(_node['contents'])

    for i in range(sphere_count):
        sphere = spheres[sphere_ids[contents + i]]
        
        testPos = sphere['x']
        if axis == 1:
            testPos = sphere['y']
        elif axis == 2:
            testPos = sphere['z']

        cost = evaluate_sah(nodes, spheres, sphere_ids, node_index, axis, testPos, bins)

        if cost < bestCost:
            bestPos = testPos
            bestCost = cost

    return (bestPos, bestCost)

@njit(cache=True)
def evaluate_sah(nodes: np.ndarray,
    spheres: np.ndarray,
    sphere_ids: np.ndarray,
    node_index: int, axis: int, split_position: float,
    bins: np.ndarray) -> float:

    bins[48]['min_x'] = 1e10
    bins[48]['min_y'] = 1e10
    bins[48]['min_z'] = 1e10
    bins[48]['sphere_count'] = 0
    bins[48]['max_x'] = -1e10
    bins[48]['max_y'] = -1e10
    bins[48]['max_z'] = -1e10
    bins[48]['contents'] = -1

    bins[49]['min_x'] = 1e10
    bins[49]['min_y'] = 1e10
    bins[49]['min_z'] = 1e10
    bins[49]['sphere_count'] = 0
    bins[49]['max_x'] = -1e10
    bins[49]['max_y'] = -1e10
    bins[49]['max_z'] = -1e10
    bins[49]['contents'] = -1

    sphere_count = int(nodes[node_index]['sphere_count'])
    contents = int(nodes[node_index]['contents'])

    for i in range(sphere_count):
        sphere = spheres[sphere_ids[contents + i]]
        #get sphere info
        s_x = sphere['x']
        s_y = sphere['y']
        s_z = sphere['z']
        s_r = sphere['radius']

        s_pos = sphere['x']
        if axis == 1:
            s_pos = sphere['y']
        elif axis == 2:
            s_pos = sphere['z']
        
        if s_pos < split_position:
            #Grow left box
            bins[48]['min_x'] = min(bins[48]['min_x'], s_x - s_r)
            bins[48]['min_y'] = min(bins[48]['min_y'], s_y - s_r)
            bins[48]['min_z'] = min(bins[48]['min_z'], s_z - s_r)
            bins[48]['sphere_count'] = bins[48]['sphere_count'] + 1
            bins[48]['max_x'] = max(bins[48]['max_x'], s_x + s_r)
            bins[48]['max_y'] = max(bins[48]['max_y'], s_y + s_r)
            bins[48]['max_z'] = max(bins[48]['max_z'], s_z + s_r)
        else:
            #Grow right box
            bins[49]['min_x'] = min(bins[49]['min_x'], s_x - s_r)
            bins[49]['min_y'] = min(bins[49]['min_y'], s_y - s_r)
            bins[49]['min_z'] = min(bins[49]['min_z'], s_z - s_r)
            bins[49]['sphere_count'] = bins[49]['sphere_count'] + 1
            bins[49]['max_x'] = max(bins[49]['max_x'], s_x + s_r)
            bins[49]['max_y'] = max(bins[49]['max_y'], s_y + s_r)
            bins[49]['max_z'] = max(bins[49]['max_z'], s_z + s_r)
    
    l_x = bins[48]['max_x'] - bins[48]['min_x']
    l_y = bins[48]['max_y'] - bins[48]['min_y']
    l_z = bins[48]['max_z'] - bins[48]['min_z']
    l_c = int(bins[48]['sphere_count'])

    #unpack right box
    r_x = bins[49]['max_x'] - bins[49]['min_x']
    r_y = bins[49]['max_y'] - bins[49]['min_y']
    r_z = bins[49]['max_z'] - bins[49]['min_z']
    r_c = int(bins[49]['sphere_count'])

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

    _node = nodes[node_index]

    bestPos = 0
    bestCost = 1e10

    testPos = _node['min_x']
    extent = _node['max_x'] - testPos
    if axis == 1:
        testPos = _node['min_y']
        extent = _node['max_y'] - testPos
    elif axis == 2:
        testPos = _node['min_z']
        extent = _node['max_z'] - testPos
    
    scale = extent / bin_count
    left_index = 16
    right_index = 32
    for i in range(bin_count):

        #unpack left box
        left_bin = bins[left_index]
        l_x = left_bin['max_x'] - left_bin['min_x']
        l_y = left_bin['max_y'] - left_bin['min_y']
        l_z = left_bin['max_z'] - left_bin['min_z']
        l_c = int(left_bin['sphere_count'])

        #unpack right box
        right_bin = bins[right_index]
        r_x = right_bin['max_x'] - right_bin['min_x']
        r_y = right_bin['max_y'] - right_bin['min_y']
        r_z = right_bin['max_z'] - right_bin['min_z']
        r_c = int(right_bin['sphere_count'])

        left_index = left_index + 1
        right_index = right_index + 1

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
    _node = nodes[node_index]
    #extract node info

    min_bound = _node['min_x']
    max_bound = _node['max_x']
    if axis == 1:
        min_bound = _node['min_y']
        max_bound = _node['max_y']
    if axis == 2:
        min_bound = _node['min_z']
        max_bound = _node['max_z']
    
    first = int(_node['contents'])
    sphere_count = int(_node['sphere_count'])

    extent = max_bound - min_bound
    bin_size = extent / bin_count
    for i in range(sphere_count):
        sphere = spheres[sphere_ids[first + i]]

        sphere_center = sphere['x']
        if axis == 1:
            sphere_center = sphere['y']
        elif axis == 2:
            sphere_center = sphere['z']
        
        #unpack sphere info
        s_x = sphere['x']
        s_y = sphere['y']
        s_z = sphere['z']
        s_r = sphere['radius']
        
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

    dl_index = 48
    dr_index = 49

    for i in range(bin_count):

        #get bin info
        bin_index = i
        left_index = (i + 16)
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
        #bins[left_index] = bins[dl_index]
        bins[left_index]['min_x'] = bins[dl_index]['min_x']
        bins[left_index]['min_y'] = bins[dl_index]['min_y']
        bins[left_index]['min_z'] = bins[dl_index]['min_z']
        bins[left_index]['sphere_count'] = bins[dl_index]['sphere_count']
        bins[left_index]['max_x'] = bins[dl_index]['max_x']
        bins[left_index]['max_y'] = bins[dl_index]['max_y']
        bins[left_index]['max_z'] = bins[dl_index]['max_z']

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
        #bins[right_index] = bins[dr_index]
        bins[right_index]['min_x'] = bins[dr_index]['min_x']
        bins[right_index]['min_y'] = bins[dr_index]['min_y']
        bins[right_index]['min_z'] = bins[dr_index]['min_z']
        bins[right_index]['sphere_count'] = bins[dr_index]['sphere_count']
        bins[right_index]['max_x'] = bins[dr_index]['max_x']
        bins[right_index]['max_y'] = bins[dr_index]['max_y']
        bins[right_index]['max_z'] = bins[dr_index]['max_z']

def object_split(nodes: np.ndarray, 
    spheres: np.ndarray, 
    sphere_ids: np.ndarray, 
    parent_index: int, axis: int, 
    nodes_used: int, split_position: float,
    bins: np.ndarray) -> int:

    _node = nodes[parent_index]
    sphere_count = int(_node['sphere_count'])
    contents = int(_node['contents'])

    #split group into halves
    i = contents
    j = i + sphere_count - 1
    while i <= j:
        sphere = spheres[sphere_ids[i]]

        sphere_center = sphere['x']
        if axis == 1:
            sphere_center = sphere['y']
        elif axis == 2:
            sphere_center = sphere['z']
        
        if sphere_center < split_position:
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
#---- BVH Updating                   ----#
#region
@njit(cache = True)
def refit_bvh(nodes: np.ndarray, 
    spheres: np.ndarray,
    sphere_ids: np.ndarray,
    node_count: int) -> None:

    i = node_count - 1
    for _ in range(node_count):
        
        #Fetch node info
        _node = nodes[i]
        count = int(_node['sphere_count'])
        first = int(_node['contents'])

        #reset node bounds
        nodes[i]['min_x'] = 1e10
        nodes[i]['min_y'] = 1e10
        nodes[i]['min_z'] = 1e10
        nodes[i]['max_x'] = -1e10
        nodes[i]['max_y'] = -1e10
        nodes[i]['max_z'] = -1e10

        if count > 0:
            #Exernal node, check spheres
            for j in range(count):

                sphere_index = sphere_ids[first + j]

                #grab sphere info
                sphere = spheres[sphere_index]
                s_x = sphere['x']
                s_y = sphere['y']
                s_z = sphere['z']
                s_r = sphere['radius']

                #find new minimum
                nodes[i]['min_x'] = min(nodes[i]['min_x'], s_x - s_r)
                nodes[i]['min_y'] = min(nodes[i]['min_y'], s_y - s_r)
                nodes[i]['min_z'] = min(nodes[i]['min_z'], s_z - s_r)
                
                #find new maximum
                nodes[i]['max_x'] = max(nodes[i]['max_x'], s_x + s_r)
                nodes[i]['max_y'] = max(nodes[i]['max_y'], s_y + s_r)
                nodes[i]['max_z'] = max(nodes[i]['max_z'], s_z + s_r)
        else:
            #Internal node, check children
            for j in range(2):

                child_node = nodes[first + j]

                #find new minimum
                nodes[i]['min_x'] = min(nodes[i]['min_x'], child_node['min_x'])
                nodes[i]['min_y'] = min(nodes[i]['min_y'], child_node['min_y'])
                nodes[i]['min_z'] = min(nodes[i]['min_z'], child_node['min_z'])
                
                #find new maximum
                nodes[i]['max_x'] = max(nodes[i]['max_x'], child_node['max_x'])
                nodes[i]['max_y'] = max(nodes[i]['max_y'], child_node['max_y'])
                nodes[i]['max_z'] = max(nodes[i]['max_z'], child_node['max_z'])

        i = i - 1
#endregion