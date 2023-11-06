from config import *

@njit(cache = True)
def make_nodes(count: int) -> np.ndarray:

    nodes = np.zeros(count, dtype=data_type_bvh_node)

    for i in range(count):

        nodes[i]['min_x'] = 1e10
        nodes[i]['min_y'] = 1e10
        nodes[i]['min_z'] = 1e10
        nodes[i]['sphere_count'] = 0
        nodes[i]['max_x'] = -1e10
        nodes[i]['max_y'] = -1e10
        nodes[i]['max_z'] = -1e10
        nodes[i]['contents'] = -1
    
    return nodes

@njit(cache = True)
def make_node() -> np.ndarray:

    _node = np.zeros(1, dtype = data_type_bvh_node)

    _node[0]['min_x'] = 1e10
    _node[0]['min_y'] = 1e10
    _node[0]['min_z'] = 1e10
    _node[0]['sphere_count'] = 0
    _node[0]['max_x'] = -1e10
    _node[0]['max_y'] = -1e10
    _node[0]['max_z'] = -1e10
    _node[0]['contents'] = -1
    
    return _node

@njit(cache = True)
def reset_nodes(nodes: np.ndarray, offset: int, count: int) -> None:

    for i in range(count):

        nodes[offset + i]['min_x'] = 1e10
        nodes[offset + i]['min_y'] = 1e10
        nodes[offset + i]['min_z'] = 1e10
        nodes[offset + i]['sphere_count'] = 0
        nodes[offset + i]['max_x'] = -1e10
        nodes[offset + i]['max_y'] = -1e10
        nodes[offset + i]['max_z'] = -1e10
        nodes[offset + i]['contents'] = -1

def print_node(node: np.record, index: int) -> None:

    min_x           = node['min_x']
    min_y           = node['min_y']
    min_z           = node['min_z']
    sphere_count    = int(node['sphere_count'])
    max_x           = node['max_x']
    max_y           = node['max_y']
    max_z           = node['max_z']
    contents        = int(node['contents'])

    e_x = max_x - min_x
    e_y = max_y - min_y
    e_z = max_z - min_z


    result = ""
    if sphere_count == 0:
        node_type = "Internal"
        sphere_count = 2
    else:
        node_type = "External"
    cost = sphere_count * (e_x * e_y + e_y * e_z + e_x * e_z)
    
    result += f"---- {node_type} Node: {index} ----\n"

    result += f"\t({min_x}, {min_y}, {min_z})"
    result += f" -> ({max_x}, {max_y}, {max_z})\n"

    result += f"\tCost: {cost}\n"
    if node_type == "Internal":
        result += f"\tLeft Child: {contents}, Right Child: {contents + 1}"
    else:
        result += f"\tSphere Count: {sphere_count}"
        result += f"\tFirst Sphere: {contents}, Last Sphere: {contents + sphere_count - 1}"
    
    print(result)
