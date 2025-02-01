from config import *

@njit(cache = True)
def make_nodes(count: int) -> np.ndarray:

    nodes = np.zeros(count,dtype = DATA_TYPE_NODE)

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

    _node = np.zeros(1, dtype = DATA_TYPE_NODE)

    _node[0]['min_x'] = 1e10
    _node[0]['min_y'] = 1e10
    _node[0]['min_z'] = 1e10
    _node[0]['sphere_count'] = 0
    _node[0]['max_x'] = -1e10
    _node[0]['max_y'] = -1e10
    _node[0]['max_z'] = -1e10
    _node[0]['contents'] = -1
    
    return _node[0]

@njit(cache = True)
def reset_node(_node: np.ndarray) -> None:

    _node['min_x'] = 1e10
    _node['min_y'] = 1e10
    _node['min_z'] = 1e10
    _node['sphere_count'] = 0
    _node['max_x'] = -1e10
    _node['max_y'] = -1e10
    _node['max_z'] = -1e10
    _node['contents'] = -1

@njit(cache = True)
def reset_nodes(nodes: np.ndarray, offset: int, count: int) -> None:

    for i in range(count):
        nodes[i]['min_x'] = 1e10
        nodes[i]['min_y'] = 1e10
        nodes[i]['min_z'] = 1e10
        nodes[i]['sphere_count'] = 0
        nodes[i]['max_x'] = -1e10
        nodes[i]['max_y'] = -1e10
        nodes[i]['max_z'] = -1e10
        nodes[i]['contents'] = -1

def print_node(nodes: np.ndarray, index: int) -> None:

    _node = nodes[index]
    min_x           = _node['min_x']
    min_y           = _node['min_y']
    min_z           = _node['min_z']
    sphere_count    = int(_node['sphere_count'])
    max_x           = _node['max_x']
    max_y           = _node['max_y']
    max_z           = _node['max_z']
    contents        = int(_node['contents'])

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
