############################## Imports   ######################################
#region
from config import *
#endregion
############################## helper functions ###############################
#region
@njit(cache = True)
def update_positions(
    instance_types: np.ndarray,
    positions: tuple[np.ndarray], 
    transforms: tuple[np.ndarray],
    light_data: np.ndarray, 
    count: int) -> None:
    """
        Write the transform matrices to the given array.
    """

    cubes_written = 0
    lights_written = 0
    for i in range(count):

        _id = positions[0][i]
        _type = instance_types[_id]
        write_index = lights_written
        if _type == 0:
            write_index = cubes_written

        #unpack position data
        index = 3 * i
        read_array = positions[1]
        x    = read_array[index]
        y    = read_array[index + 1]
        z    = read_array[index + 2]

        #write transforms
        if (has_components[_type] & 1):
            index = 16 * write_index
            target_array = transforms[_type]

            target_array[index]      = 1.0
            target_array[index + 5]  = 1.0
            target_array[index + 10] = 1.0
            target_array[index + 12] = x
            target_array[index + 13] = y
            target_array[index + 14] = z
            target_array[index + 15] = 1.0

        #write light position
        if (has_components[_type] & (1 << 2)):

            index = 8 * write_index
            target_array = light_data

            target_array[index]     = x
            target_array[index + 1] = y
            target_array[index + 2] = z

        if _type == 0:
            cubes_written += 1
        else:
            lights_written += 1

@njit(cache = True)
def update_eulers(
    eulers: np.ndarray, transforms: np.ndarray, 
    count: int, rate: float) -> None:
    """
        Update all those cubes! Also, write the transform matrices to the given array.
    """

    for i in range(count):

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

        #write transforms
        index = 16 * i

        r_y = np.radians(e_y)
        r_z = np.radians(e_z)
        c_y = np.cos(r_y)
        s_y = np.sin(r_y)
        c_z = np.cos(r_z)
        s_z = np.sin(r_z)

        transforms[index]      = c_y * c_z
        transforms[index + 1]  = c_y * s_z
        transforms[index + 2]  = -s_y
        transforms[index + 4]  = -s_z
        transforms[index + 5]  = c_z
        transforms[index + 8]  = s_y * c_z
        transforms[index + 9]  = s_y * s_z
        transforms[index + 10] = c_y

        #write euler data back
        index = 6 * i
        eulers[index]     = e_x
        eulers[index + 1] = e_y
        eulers[index + 2] = e_z

@njit(cache = True)
def update_lights(
    lights: tuple[np.ndarray],
    light_data:np.ndarray, count: int) -> None:
    """
        Write the light data to the given array.
        Lights don't have much updating to do.
    """

    for i in range(count):

        #unpack light color and strength
        index = 4 * i
        r     = lights[1][index]
        g     = lights[1][index + 1]
        b     = lights[1][index + 2]
        s     = lights[1][index + 3]

        #write light data
        index = 8 * i

        light_data[index + 4] = r
        light_data[index + 5] = g
        light_data[index + 6] = b
        light_data[index + 7] = s

@njit(cache = True)
def move_player(player: np.ndarray, d_pos: np.ndarray) -> None:
    """
        Move by the given amount in the (forwards, right, up) vectors.
    """

    x = player[0]
    y = player[1]
    z = player[2]

    for i in range(3):

        x += d_pos[i] * player[6 + 3 * i]
        y += d_pos[i] * player[7 + 3 * i]
        z += d_pos[i] * player[8 + 3 * i]

    player[0] = x
    player[1] = y
    player[2] = z

@njit(cache = True)
def spin_player(player: np.ndarray, d_eulers: np.ndarray) -> None:
    """
        Spin the camera by the given amount about the (x, y, z) axes.
    """

    e_x = player[3] + d_eulers[0]
    e_y = player[4] + d_eulers[1]
    e_z = player[5] + d_eulers[2]


    player[3] = e_x % 360
    player[4] = min(89, max(-89, e_y))
    player[5] = e_z % 360

@njit(cache = True)
def update_player(player: tuple[np.ndarray]) -> None:
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
############################### Data Schema ###################################
#region
#---- Internal ----#
"""
    instance types:

    id(implicit): int
    obj_type: int
"""
"""
    deleted ids:
    id(implicit): int
"""
has_components: np.ndarray = np.array((3,5), dtype = np.uint8)
#CUBE: transform: true, eulers: true, light: false
#LIGHT: transform: true, eulers: false, light: true
"""
    positions:

    id: int
    pos: vec3
"""
"""
    eulers:

    id: int
    eulers: vec3
    euler_velocity: vec3
"""
"""
    lights

    id: int
    color: vec3
    strength: float
"""
#---- Hybrid ----#
"""
    Camera:
    position: 3
    eulers: 3
    forwards: 3
    right: 3
    up: 3

    stride: 15
"""
#---- Output ----#
"""
    Transform:

    stride: 16
"""
"""
    Light Data:
    pos, color, strength

    stride: 7
"""
"""
    View:

    stride: 16
"""
#endregion
##################################### Model ###################################
#region
class Scene:
    """
        Manages all objects and coordinates their interactions.
    """
    __slots__ = (
        "entity_counts", "instances_made", "instance_types", 
        "deleted_ids",
        "positions", "eulers", "lights", "player", "model_transforms", 
        "light_data")


    def __init__(self):
        """
            Initialize the scene.
        """

        self.entity_counts: dict[int, int] = {
            ENTITY_TYPE["CUBE"]: 0,
            ENTITY_TYPE["POINTLIGHT"]: 0
        }

        self._make_internal_objects()

        #Hybrid Data
        self.player: list[np.ndarray] = [
            np.zeros(15, dtype = np.float32),
            np.zeros(16, dtype = np.float32)
        ]
        self._make_player()

        self._make_output_data()
    
    def _make_internal_objects(self) -> None:

        self.instances_made = 0
        self.instance_types: np.ndarray = np.array([], dtype=np.uint8)
        self.deleted_ids: np.array = np.array([], dtype = np.uint16)
        self.positions: list[np.ndarray] = [
            np.array([], dtype=np.uint16),
            np.array([], dtype=np.float32)
        ]
        self.eulers: list[np.ndarray] = [
            np.array([], dtype=np.uint16),
            np.array([], dtype=np.float32),
        ]
        self.lights: list[np.array] = [
            np.array([], dtype=np.uint16),
            np.array([], dtype=np.float32),
        ]
        self._make_cubes()
        self._make_lights()

    def _make_cubes(self) -> None:
        """
            Make the cubes!
        """

        for _ in range(200):

            x = np.random.uniform(low = -10, high = 10)
            y = np.random.uniform(low = -10, high = 10)
            z = np.random.uniform(low = -10, high = 10)
            self.positions[0] = np.append(self.positions[0], self.instances_made)
            self.positions[1] = np.append(self.positions[1], (x, y, z))

            e_x = np.random.uniform(low = 0, high = 360)
            e_y = np.random.uniform(low = 0, high = 360)
            e_z = np.random.uniform(low = 0, high = 360)
            ev_x = np.random.uniform(low = -0.2, high = 0.2)
            ev_y = np.random.uniform(low = -0.2, high = 0.2)
            ev_z = np.random.uniform(low = -0.2, high = 0.2)
            self.eulers[0] = np.append(self.eulers[0], self.instances_made)
            self.eulers[1] = np.append(
                self.eulers[1], 
                (e_x, e_y, e_z, ev_x, ev_y, ev_z))
            
            self.instance_types = np.append(self.instance_types, 0)

            self.instances_made += 1
        
        self.entity_counts[ENTITY_TYPE["CUBE"]] = 200

    def _make_lights(self) -> None:
        """
            Make the lights!
        """

        for _ in range(8):

            x = np.random.uniform(low = -10, high = 10)
            y = np.random.uniform(low = -10, high = 10)
            z = np.random.uniform(low = -10, high = 10)
            self.positions[0] = np.append(
                self.positions[0], self.instances_made)
            self.positions[1] = np.append(self.positions[1], (x, y, z))

            r = np.random.uniform(low = 0.5, high = 1.0)
            g = np.random.uniform(low = 0.5, high = 1.0)
            b = np.random.uniform(low = 0.5, high = 1.0)
            s = np.random.uniform(low = 2, high = 5)

            self.lights[0] = np.append(self.lights[0], self.instances_made)
            self.lights[1] = np.append(self.lights[1], (r, g, b, s))

            self.instance_types = np.append(self.instance_types, 1)
            self.instances_made += 1
        
        self.entity_counts[ENTITY_TYPE["POINTLIGHT"]] = 8
    
    def _make_player(self) -> None:
        """
            Make the player.
        """

        x = -10
        f_x = 1.0
        r_y = -1.0
        u_z = 1.0
        #all other fields happen to be zero.

        target_array = self.player[0]
        target_array[0] = x
        target_array[6] = f_x
        target_array[10] = r_y
        target_array[14] = u_z
        
        #load identity into view transform
        target_array = self.player[1]
        for i in range(4):
            target_array[5 * i] = 1.0

    def _make_output_data(self) -> None:

        self.model_transforms: list[np.ndarray] = [
            np.zeros(16 * 200, dtype=np.float32),
            np.zeros(16 * 8, dtype=np.float32)
        ]
        self.light_data = np.zeros(8 * 8, dtype=np.float32)

        update_player((self.player[0], self.player[1]))
        update_lights(
            lights = (self.lights[0], self.lights[1]),
            light_data = self.light_data,
            count = 8
        )
        update_positions(
            instance_types = self.instance_types,
            positions = (self.positions[0], self.positions[1]),
            transforms = (self.model_transforms[0], self.model_transforms[1]),
            light_data = self.light_data,
            count = 208
        )

    def update(self, dt: float) -> None:
        """
            Update all objects in the scene.

            Parameters:

                dt: framerate correction factor
        """

        update_eulers(
            eulers = self.eulers[1],
            transforms = self.model_transforms[0],
            count = 200, rate = dt
        )

        update_player((self.player[0], self.player[1]))

    def move_player(self, d_pos: list[float]) -> None:
        """
            move the player by the given amount in the 
            (forwards, right, up) vectors.
        """

        move_player(self.player[0], d_pos)
    
    def spin_player(self, d_eulers: list[float]) -> None:
        """
            spin the player by the given amount
            around the (x,y,z) axes
        """

        spin_player(self.player[0], d_eulers)
#endregion
###############################################################################