############################## Imports   ######################################
#region
from config import *
#endregion
############################### Tables      ###################################
#region
has_components: np.ndarray = np.array((3,5), dtype = np.uint8)
#CUBE: transform: true, eulers: true, light: false
#LIGHT: transform: true, eulers: false, light: true
entity_counts = np.zeros(2, dtype=np.uint16)
table_counts = np.zeros(8, dtype=np.uint16)
table_sizes = np.zeros(8, dtype=np.uint16)
tables: list[np.ndarray] = []
"""
    instance ids:

    id: int
    obj_type: int
"""
tables.append(np.array([], dtype=np.uint16))
tables.append(np.array([], dtype=np.uint16))
"""
    deleted ids:
    id(implicit): int
"""
tables.append(np.array([], dtype=np.uint16))
"""
    positions:

    id: int
    pos: vec3
"""
tables.append(np.array([], dtype=np.uint16))
tables.append(np.array([], dtype=np.float32))
"""
    eulers:

    id: int
    eulers: vec3
    euler_velocity: vec3
"""
tables.append(np.array([], dtype=np.uint16))
tables.append(np.array([], dtype=np.float32))
"""
    lights

    id: int
    color: vec3
    strength: float
"""
tables.append(np.array([], dtype=np.uint16))
tables.append(np.array([], dtype=np.float32))
#---- Hybrid ----#
"""
    Camera:
    position: 3
    eulers: 3
    forwards: 3
    right: 3
    up: 3

    stride: 15

    View:

    stride: 16
"""
player: list[np.ndarray] = [
    np.zeros(15, dtype = np.float32),
    np.zeros(16, dtype = np.float32)
]
#---- Output ----#
"""
    Transform:

    stride: 16
"""
tables.append(np.array([], dtype=np.uint16))
tables.append(np.array([], dtype=np.float32))
tables.append(np.array([], dtype=np.uint16))
tables.append(np.array([], dtype=np.float32))
"""
    Light Data:
    pos, color, strength

    stride: 7
"""
tables.append(np.array([], dtype=np.uint16))
tables.append(np.array([], dtype=np.float32))
#endregion
############################## instances        ###############################
#region
def add_instance(_id: int, _type: int) -> None:
    """
        Attempts to register an instance with the given id and type,
        resizing if necessary.
    """

    ids   = tables[0]
    types = tables[1]

    size  = table_sizes[0]
    count = table_counts[0]

    if count >= size:

        #reallocate!
        new_size  = max(2 * size, 1)

        new_array = np.zeros(new_size, dtype = np.uint16)
        new_array[0:size] = ids[:]
        tables[0]         = new_array
        ids               = new_array

        new_array = np.zeros(new_size, dtype = np.uint16)
        new_array[0:size] = types[:]
        tables[1]         = new_array
        types             = new_array

        table_sizes[0] = new_size
    
    ids[count]       = _id
    types[count]     = _type
    table_counts[0] += 1

def remove_instance(_id: int) -> None:
    """
        Attempts to remove an instance with the given id
    """

    ids   = tables[0]
    types = tables[1]

    count = table_counts[0]
    if count == 0:
        return
    
    i = np.where(ids == _id)
    if len(i[0]) == 0:
        return
    i = i[0][0]
    
    #swap ids
    ids[i] = ids[count - 1]

    #swap types
    types[i] = types[count - 1]

    #decrement count
    table_counts[0] -= 1
#endregion
############################## garbage bin      ###############################
#region
def add_deleted_id(_id: int) -> None:
    """
        Attempts to record an id to the garbage bin,
        resizing if necessary.
    """

    deleted_ids = tables[2]

    size  = table_sizes[1]
    count = table_counts[1]
    if count >= size:

        #reallocate!
        new_size  = max(2 * size, 1)
        new_array = np.zeros(new_size, dtype = np.uint16)

        new_array[0:size] = deleted_ids[:]
        
        tables[2]      = new_array
        table_sizes[1] = new_size
        deleted_ids    = new_array
    
    deleted_ids[count] = _id
    table_counts[1]   += 1

def reuse_id() -> int:
    """
        Returns the id of a previously deleted object, if it exists.
        Returns -1 otherwise.
    """

    deleted_ids = tables[2]
    count       = table_counts[1]

    if count == 0:
        return -1
    
    _id              = deleted_ids[count - 1]
    table_counts[1] -= 1
    return _id
#endregion
############################## positions        ###############################
#region
def add_position(_id: int, pos: np.ndarray) -> None:
    """
        Attempts to register an instance with the given id and position,
        resizing if necessary.
    """

    ids          = tables[3]
    positions    = tables[4]

    size  = table_sizes[2]
    count = table_counts[2]
    if count >= size:

        #reallocate!
        new_size = max(2 * size, 1)

        new_array         = np.zeros(new_size, dtype = np.uint16)
        new_array[0:size] = ids[:]
        tables[3]         = new_array
        ids               = new_array

        new_array             = np.zeros(3 * new_size, dtype = np.float32)
        new_array[0:3 * size] = positions[:]
        tables[4]             = new_array
        positions             = new_array

        table_sizes[2] = new_size
    
    ids[count]                             = _id
    positions[3 * count : 3 * (count + 1)] = pos[:]
    table_counts[2]                       += 1

def update_positions() -> None:
    """
        Write the transform matrices to the given array.
    """

    instance_ids   = tables[0]
    instance_types = tables[1]
    position_ids   = tables[3]
    positions      = tables[4]

    count = table_counts[2]

    for i in range(count):

        _id   = position_ids[i]
        j     = np.where(instance_ids == _id)[0][0]
        _type = instance_types[j]

        #unpack position data
        index = 3 * i
        x     = positions[index]
        y     = positions[index + 1]
        z     = positions[index + 2]

        #write transforms
        for _ in range(has_components[_type] & 1):

            target_array = tables[9 + 2 * _type]
            write_index  = np.where(target_array == _id)[0][0]
            index        = 16 * write_index
            target_array = tables[10 + 2 * _type]

            target_array[index]      = 1.0
            target_array[index + 5]  = 1.0
            target_array[index + 10] = 1.0
            target_array[index + 12] = x
            target_array[index + 13] = y
            target_array[index + 14] = z
            target_array[index + 15] = 1.0

        #write light position
        for _ in range((has_components[_type] & (1 << 2)) >> 2):
            write_index  = np.where(tables[13] == _id)[0][0]
            index        = 8 * write_index
            target_array = tables[14]

            target_array[index]     = x
            target_array[index + 1] = y
            target_array[index + 2] = z

def remove_position(_id: int) -> None:
    """
        Remove the given id from the positions.
    """

    position_ids = tables[3]
    positions    = tables[4]

    count = table_counts[2]
    if count == 0:
        return
    
    i = np.where(position_ids == _id)
    if len(i[0]) == 0:
        return
    i = i[0][0]
    
    #swap indices
    position_ids[i] = position_ids[count - 1]

    #swap positions
    positions[(3 * i) : (3 * i + 3)] = positions[(3 * count - 3) : (3 * count)]

    #decrement count
    table_counts[2] -= 1
#endregion
############################## eulers           ###############################
#region
def add_eulers(_id: int, entry: np.ndarray) -> None:
    """
        Attempts to register an instance with the given id and eulers,
        resizing if necessary.
    """

    euler_ids = tables[5]
    eulers    = tables[6]

    size  = table_sizes[3]
    count = table_counts[3]

    if count >= size:

        #reallocate!
        new_size = max(2 * size, 1)

        new_array         = np.zeros(new_size, dtype = np.uint16)
        new_array[0:size] = euler_ids[:]
        tables[5]         = new_array
        euler_ids         = new_array

        new_array             = np.zeros(6 * new_size, dtype = np.float32)
        new_array[0:6 * size] = eulers[:]
        tables[6]             = new_array
        eulers                = new_array

        table_sizes[3] = new_size
    
    euler_ids[count]                    = _id
    eulers[6 * count : 6 * (count + 1)] = entry[:]
    table_counts[3]                    += 1

def update_eulers(rate: float) -> None:
    """
        Update all those cubes! Also, write the transform matrices to the given array.
    """

    euler_ids = tables[5]
    eulers    = tables[6]

    count = table_counts[3]

    for i in range(count):

        _id = euler_ids[i]

        #unpack cube data
        index = 6 * i
        e_x  = eulers[index]
        e_y  = eulers[index + 1]
        e_z  = eulers[index + 2]
        ev_x = eulers[index + 3]
        ev_y = eulers[index + 4]
        ev_z = eulers[index + 5]

        #update cube data
        e_x = (e_x + rate * ev_x) % 360
        e_y = (e_y + rate * ev_y) % 360
        e_z = (e_z + rate * ev_z) % 360

        #write euler data back
        eulers[index]     = e_x
        eulers[index + 1] = e_y
        eulers[index + 2] = e_z

        #write transforms
        write_index = np.where(tables[9] == _id)[0][0]
        index = 16 * write_index

        r_y = np.radians(e_y)
        r_z = np.radians(e_z)
        c_y = np.cos(r_y)
        s_y = np.sin(r_y)
        c_z = np.cos(r_z)
        s_z = np.sin(r_z)

        target_array             = tables[10]
        target_array[index]      = c_y * c_z
        target_array[index + 1]  = c_y * s_z
        target_array[index + 2]  = -s_y
        target_array[index + 4]  = -s_z
        target_array[index + 5]  = c_z
        target_array[index + 8]  = s_y * c_z
        target_array[index + 9]  = s_y * s_z
        target_array[index + 10] = c_y

def remove_eulers(_id: int) -> None:
    """
        Remove the given id from the positions.
    """

    euler_ids = tables[5]
    eulers    = tables[6]

    count = table_counts[3]
    if count == 0:
        return
    
    i = np.where(euler_ids == _id)
    if len(i[0]) == 0:
        return
    i = i[0][0]
    
    #swap indices
    euler_ids[i] = euler_ids[count - 1]

    #swap positions
    eulers[6*i : 6 * (i + 1)] = eulers[6 * (count - 1) : 6 * count]

    #decrement count
    table_counts[3] -= 1
#endregion
############################## lights           ###############################
#region
def add_light(_id: int, light: np.ndarray) -> None:
    """
        Attempts to register an instance with the given id and eulers,
        resizing if necessary.
    """

    ids = tables[7]
    lights    = tables[8]

    size  = table_sizes[4]
    count = table_counts[4]

    if count >= size:

        #reallocate!
        new_size = max(2 * size, 1)

        new_array         = np.zeros(new_size, dtype = np.uint16)
        new_array[0:size] = ids[:]
        tables[7]         = new_array
        ids               = new_array

        new_array             = np.zeros(4 * new_size, dtype = np.float32)
        new_array[0:4 * size] = lights[:]
        tables[8]             = new_array
        lights                = new_array

        table_sizes[4] = new_size
    
    ids[count]                          = _id
    lights[4 * count : 4 * (count + 1)] = light[:]
    table_counts[4]                    += 1

def update_lights() -> None:
    """
        Write the light data to the given array.
        Lights don't have much updating to do.
    """

    ids    = tables[7]
    lights = tables[8]

    count = table_counts[4]

    for i in range(count):

        _id = ids[i]

        #unpack light color and strength
        index = 4 * i
        r     = lights[index]
        g     = lights[index + 1]
        b     = lights[index + 2]
        s     = lights[index + 3]

        #write light data
        write_index = np.where(tables[13] == _id)[0][0]
        index = 8 * write_index

        target_array            = tables[14]
        target_array[index + 4] = r
        target_array[index + 5] = g
        target_array[index + 6] = b
        target_array[index + 7] = s

def remove_light(_id: int) -> None:
    """
        Remove the given light
    """

    ids    = tables[7]
    lights = tables[8]

    count = table_counts[4]
    if count == 0:
        return
    
    i = np.where(ids == _id)
    if len(i[0]) == 0:
        return
    i = i[0][0]
    
    #swap indices
    ids[i] = ids[count - 1]

    #swap positions
    lights[4*i : 4 * (i + 1)] = lights[4 * (count - 1) : 4 * count]

    #decrement count
    table_counts[4] -= 1
#endregion
############################## Player           ###############################
#region
def move_player(d_pos: np.ndarray) -> None:
    """
        Move by the given amount in the (forwards, right, up) vectors.
    """

    target_array = player[0]
    x = target_array[0]
    y = target_array[1]
    z = target_array[2]

    for i in range(3):

        x += d_pos[i] * target_array[6 + 3 * i]
        y += d_pos[i] * target_array[7 + 3 * i]
        z += d_pos[i] * target_array[8 + 3 * i]

    target_array[0] = x
    target_array[1] = y
    target_array[2] = z

def spin_player(d_eulers: np.ndarray) -> None:
    """
        Spin the camera by the given amount about the (x, y, z) axes.
    """

    target_array = player[0]
    e_x = target_array[3] + d_eulers[0]
    e_y = target_array[4] + d_eulers[1]
    e_z = target_array[5] + d_eulers[2]


    target_array[3] = e_x % 360
    target_array[4] = min(89, max(-89, e_y))
    target_array[5] = e_z % 360

def update_player() -> None:
    """
        Update the camera, write its view transform also.
    """

    target_array = player[0]
    e_y = target_array[4]
    e_z = target_array[5]

    c_y = np.cos(np.radians(e_y))
    s_y = np.sin(np.radians(e_y))
    c_z = np.cos(np.radians(e_z))
    s_z = np.sin(np.radians(e_z))

    f_x = c_z * c_y
    f_y = s_z * c_y
    f_z = s_y
    norm = np.sqrt(f_x * f_x + f_y * f_y + f_z * f_z)
    f_x = f_x / norm
    f_y = f_y / norm
    f_z = f_z / norm

    r_x = f_y
    r_y = -f_x
    r_z = 0.0
    norm = np.sqrt(r_x * r_x + r_y * r_y + r_z * r_z)
    r_x = r_x / norm
    r_y = r_y / norm
    r_z = r_z / norm

    u_x = r_y * f_z - r_z * f_y
    u_y = r_z * f_x - r_x * f_z
    u_z = r_x * f_y - r_y * f_x
    norm = np.sqrt(u_x * u_x + u_y * u_y + u_z * u_z)
    u_x = u_x / norm
    u_y = u_y / norm
    u_z = u_z / norm

    target_array[6] = f_x
    target_array[7] = f_y
    target_array[8] = f_z
    target_array[9] = r_x
    target_array[10] = r_y
    target_array[11] = r_z
    target_array[12] = u_x
    target_array[13] = u_y
    target_array[14] = u_z

    x = target_array[0]
    y = target_array[1]
    z = target_array[2]

    target_array = player[1]
    target_array[0] = r_x
    target_array[1] = u_x
    target_array[2] = -f_x
    target_array[4] = r_y
    target_array[5] = u_y
    target_array[6] = -f_y
    target_array[8] = r_z
    target_array[9] = u_z
    target_array[10] = -f_z
    target_array[12] = -(r_x * x + r_y * y + r_z * z)
    target_array[13] = -(u_x * x + u_y * y + u_z * z)
    target_array[14] = f_x * x + f_y * y + f_z * z
    target_array[15] = 1.0
#endregion
############################## Model Transforms ###############################
#region
def add_transform(_id: int, _type: int) -> None:
    """
        Attempts to register a model transform for the given id
        and instance type.
    """

    ids        = tables[9 + 2 * _type]
    transforms = tables[10 + 2 * _type]

    size  = table_sizes[5 + _type]
    count = table_counts[5 + _type]

    if count >= size:

        #reallocate!
        new_size = max(2 * size, 1)

        new_array             = np.zeros(new_size, dtype = np.uint16)
        new_array[0:size]     = ids[:]
        tables[9 + 2 * _type] = new_array
        ids                   = new_array

        new_array              = np.zeros(16 * new_size, dtype = np.float32)
        new_array[0:16 * size] = transforms[:]
        tables[10 + 2 * _type] = new_array
        transforms             = new_array

        table_sizes[5 + _type] = new_size
    
    ids[count] = _id
    for i in range(16):
        j = 16 * count + i
        if i in (0, 5, 10, 15):
            transforms[j]    = 1.0
        else:
            transforms[j]    = 0.0
    table_counts[5 + _type] += 1

def remove_transform(_id: int, _type: int) -> None:
    """
        Remove the given transform
    """

    ids        = tables[9 + 2 * _type]
    transforms = tables[10 + 2 * _type]

    count = table_counts[5 + _type]
    if count == 0:
        return
    
    i = np.where(ids == _id)
    if len(i[0]) == 0:
        return
    i = i[0][0]
    
    #swap indices
    ids[i] = ids[count - 1]

    #swap transforms
    transforms[16*i : 16 * (i + 1)] = transforms[16 * (count - 1) : 16 * count]

    #decrement count
    table_counts[5 + _type] -= 1
#endregion
############################## Light Data       ###############################
#region
def add_light_data(_id: int) -> None:
    """
        Attempts to register a light for rendering
    """

    ids        = tables[13]
    light_data = tables[14]

    size  = table_sizes[7]
    count = table_counts[7]

    if count >= size:

        #reallocate!
        new_size = max(2 * size, 1)

        new_array         = np.zeros(new_size, dtype = np.uint16)
        new_array[0:size] = ids[:]
        tables[13]        = new_array
        ids               = new_array

        new_array             = np.zeros(8 * new_size, dtype = np.float32)
        new_array[0:8 * size] = light_data[:]
        tables[14]            = new_array
        light_data            = new_array

        table_sizes[7] = new_size
    
    ids[count] = _id
    for i in range(8):
        light_data[8 * count + i] = 0.0
    table_counts[7] += 1

def remove_light_data(_id: int) -> None:
    """
        Remove the given light data
    """

    ids    = tables[13]
    lights = tables[14]

    count = table_counts[7]
    if count == 0:
        return
    
    i = np.where(ids == _id)
    if len(i[0]) == 0:
        return
    i = i[0][0]
    
    #swap indices
    ids[i] = ids[count - 1]

    #swap light data
    lights[8*i : 8 * (i + 1)] = lights[8 * (count - 1) : 8 * count]

    #decrement count
    table_counts[7] -= 1
#endregion
##################################### Model ###################################
#region

def log_state() -> None:
    """
        Simple template for debug purposes.
    """

    print("------------------------------")
    print(f"ids: {tables[0]}")
    print(f"instance types: {tables[1]}")
    print(f"id count: {table_counts[0]}")
    print(f"id size: {table_sizes[0]}")
    print("------------------------------")
    print(f"garbage bin: {tables[2]}")
    print(f"bin count: {table_counts[1]}")
    print(f"bin size: {table_sizes[1]}")
    print("------------------------------")

def make_cube() -> None:
    """
        Make the cube!
    """

    _id = reuse_id()
    if _id < 0:
        _id = table_counts[0]

    #Register id
    add_instance(_id, 0)

    #Add position
    x = np.random.uniform(low = -10, high = 10)
    y = np.random.uniform(low = -10, high = 10)
    z = np.random.uniform(low = -10, high = 10)
    add_position(_id, np.array((x,y,z), dtype=np.float32))

    #add eulers
    e_x = np.random.uniform(low = 0, high = 360)
    e_y = np.random.uniform(low = 0, high = 360)
    e_z = np.random.uniform(low = 0, high = 360)
    ev_x = np.random.uniform(low = -0.2, high = 0.2)
    ev_y = np.random.uniform(low = -0.2, high = 0.2)
    ev_z = np.random.uniform(low = -0.2, high = 0.2)
    add_eulers(_id = _id, 
        entry = np.array(
            (e_x, e_y, e_z, ev_x, ev_y, ev_z), dtype=np.float32))

    #add model transform
    add_transform(_id, _type = 0)
    
    entity_counts[ENTITY_TYPE["CUBE"]] += 1

    #log_state()

def delete_cube() -> None:
    """
        Delete a cube!
    """

    if entity_counts[ENTITY_TYPE["CUBE"]] == 0:
        return

    #choose a random cube
    _id = 0
    print("Trying to delete a cube")
    while True:
        i = np.random.randint(
            low = 0, 
            high = table_counts[0])
        _id = tables[0][i]
        _type = tables[1][i]
        print(f"Guessed id: {_id}")
        if _type == 0:
            print("It's a cube!")
            break
    
    remove_instance(_id)
    add_deleted_id(_id)
    remove_position(_id)
    remove_eulers(_id)
    remove_transform(_id, _type = 0)
    
    entity_counts[ENTITY_TYPE["CUBE"]] -= 1
    #log_state()

def make_light() -> None:
    """
        Make a light!
    """

    _id = reuse_id()
    if _id < 0:
        _id = table_counts[0]

    #Register id
    add_instance(_id, 1)

    #Add position
    x = np.random.uniform(low = -10, high = 10)
    y = np.random.uniform(low = -10, high = 10)
    z = np.random.uniform(low = -10, high = 10)
    add_position(_id, np.array((x,y,z), dtype = np.float32))

    #add light
    r = np.random.uniform(low = 0.5, high = 1.0)
    g = np.random.uniform(low = 0.5, high = 1.0)
    b = np.random.uniform(low = 0.5, high = 1.0)
    s = np.random.uniform(low = 2, high = 5)
    add_light(_id = _id, light = np.array((r, g, b, s), dtype=np.float32))

    #add model transform
    add_transform(_id, _type = 1)

    #add light data
    add_light_data(_id)
    
    entity_counts[ENTITY_TYPE["POINTLIGHT"]] += 1
    #log_state()
    
def delete_light() -> None:
    """
        delete a light!
    """

    if entity_counts[ENTITY_TYPE["POINTLIGHT"]] == 0:
        return

    #choose a random light
    print("Trying to delete a light")
    while True:
        i = np.random.randint(
            low = 0, 
            high = table_counts[0])
        _id = tables[0][i]
        _type = tables[1][i]
        print(f"Guessed id: {_id}")
        if _type == 1:
            print("It's a light!")
            break
    
    remove_instance(_id)
    add_deleted_id(_id)
    remove_position(_id)
    remove_light(_id)

    #Remove from model transform
    remove_transform(_id, _type = 1)

    #Remove from light data
    remove_light_data(_id)
    
    entity_counts[ENTITY_TYPE["POINTLIGHT"]] -= 1
    #log_state()

def make_player() -> None:
    """
        Make the player.
    """

    x = -10
    f_x = 1.0
    r_y = -1.0
    u_z = 1.0
    #all other fields happen to be zero.

    target_array = player[0]
    target_array[0] = x
    target_array[6] = f_x
    target_array[10] = r_y
    target_array[14] = u_z
    
    #load identity into view transform
    target_array = player[1]
    for i in range(4):
        target_array[5 * i] = 1.0
    update_player()

def update(dt: float) -> None:
    """
        Update all objects in the scene.

        Parameters:

            dt: framerate correction factor
    """

    update_positions()

    update_eulers(rate = dt)

    update_lights()

    update_player()
#endregion
###############################################################################