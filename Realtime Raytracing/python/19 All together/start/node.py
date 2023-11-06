from config import *

@njit(cache = True)
def make_nodes(count: int) -> np.ndarray:

    nodes = np.zeros(8 * count,dtype = np.float32)

    default_min_corner = np.array([1e10, 1e10, 1e10], dtype=np.float32)
    default_sphere_count = 0
    default_max_corner = np.array([-1e10, -1e10, -1e10], dtype=np.float32)
    default_contents = -1

    for i in range(count):
        base_index = 8 * i
        nodes[base_index : base_index + 3] = default_min_corner.copy()
        nodes[base_index + 3] = default_sphere_count
        nodes[base_index + 4 : base_index + 7] = default_max_corner.copy()
        nodes[base_index + 7] = default_contents
    
    return nodes

@njit(cache = True)
def make_node() -> np.ndarray:

    _node = np.zeros(8, dtype = np.float32)

    _node[0] = 1e10
    _node[1] = 1e10
    _node[2] = 1e10
    _node[3] = 0
    _node[4] = -1e10
    _node[5] = -1e10
    _node[6] = -1e10
    _node[7] = -1
    
    return _node

@njit(cache = True)
def reset_node(_node: np.ndarray) -> None:

    _node[0] = 1e10
    _node[1] = 1e10
    _node[2] = 1e10
    _node[3] = 0
    _node[4] = -1e10
    _node[5] = -1e10
    _node[6] = -1e10
    _node[7] = -1

@njit(cache = True)
def reset_nodes(nodes: np.ndarray, offset: int, count: int) -> None:

    for i in range(count):

        base_index = 8 * (offset + i)
        nodes[base_index] = 1e10
        nodes[base_index + 1] = 1e10
        nodes[base_index + 2] = 1e10
        nodes[base_index + 3] = 0
        nodes[base_index + 4] = -1e10
        nodes[base_index + 5] = -1e10
        nodes[base_index + 6] = -1e10
        nodes[base_index + 7] = -1

def print_node(nodes: np.ndarray, index: int) -> None:

    base_index = index * 8
    min_x           = nodes[base_index]
    min_y           = nodes[base_index + 1]
    min_z           = nodes[base_index + 2]
    sphere_count    = int(nodes[base_index + 3])
    max_x           = nodes[base_index + 4]
    max_y           = nodes[base_index + 5]
    max_z           = nodes[base_index + 6]
    contents        = int(nodes[base_index + 7])

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
