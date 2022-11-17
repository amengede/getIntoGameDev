from config import *

@njit(cache=True)
def add_dynamic_object(
    new_x: float, new_y: float, 
    pos: np.ndarray,
    vel: np.ndarray,
    obj_count: int, max_obj_count: int) -> int:
    """
        Try to record a new dynamic object (position and velocity)

        Parameters:
            new_x: x coordinate of the object to be added
            new_y: y coordinate of the object to be added
            pos: array holding positions of objects
            vel: array holding velocities of objects
            obj_count: number of objects currently existing
            max_obj_count: maximum capacity of arrays
        
        Returns:
            The number of current objects after adding
    """
    
    if obj_count == max_obj_count:
        return obj_count
    
    pos[2 * obj_count]     = new_x
    pos[2 * obj_count + 1] = new_y
    vel[2 * obj_count] = 0.0
    vel[2 * obj_count + 1] = 0.0
    
    return obj_count + 1

@njit(cache=True)
def remove_dynamic_object(
    index: int, 
    pos: np.ndarray,
    vel: np.ndarray,
    obj_count: int) -> int:
    """
        Try to remove a dynamic object (position and velocity)

        Parameters:
            index: index of the sphere to remove
            pos: array holding positions of existing objects
            vel: array holding velocities of existing objects
            obj_count: number of objects currently existing
        
        Returns:
            The number of current objects after removal
    """

    if index <= 0 or index >= obj_count:
        return obj_count
    
    pos[2 * index] = pos[2 * (obj_count - 1)]
    pos[2 * index + 1] = pos[2 * (obj_count - 1) + 1]
    vel[2 * index] = vel[2 * (obj_count - 1)]
    vel[2 * index + 1] = vel[2 * (obj_count - 1) + 1]

    pos[2 * (obj_count - 1)] = np.nan
    pos[2 * (obj_count - 1) + 1] = np.nan
    vel[2 * (obj_count - 1)] = np.nan
    vel[2 * (obj_count - 1) + 1] = np.nan
    
    return obj_count - 1

@njit(cache=True)
def update_dynamic_objects(
    dt: float, 
    pos: np.ndarray,
    vel: np.ndarray, 
    obj_count: int) -> None:
    """
        Update dynamic objects

        Parameters:
            dt: number of seconds since last update
            pos: array holding positions of existing objects
            vel: array holding velocities of existing objects
            obj_count: number of objects currently existing
    """

    for i in range(obj_count):

        #cache variables
        vel_x = vel[2 * i]
        vel_y = vel[2 * i + 1]
        pos_x = pos[2 * i]
        pos_y = pos[2 * i + 1]

        #apply friction to velocities
        vel_x -= TABLE_FRICTION * dt * vel_x
        if np.abs(vel_x) < 1e-7:
            vel_x = 0.0
        vel_y -= TABLE_FRICTION * dt * vel_y
        if np.abs(vel_y) < 1e-7:
            vel_y = 0.0

        #update positions, check boundary conditions
        pos_x += dt * vel_x
        if pos_x - SPHERE_RADIUS <= 0:
            pos_x = SPHERE_RADIUS
            vel_x = -vel_x
        if pos_x + SPHERE_RADIUS >= TABLE_LENGTH:
            pos_x = TABLE_LENGTH - SPHERE_RADIUS
            vel_x = -vel_x
        
        pos_y += dt * vel_y
        if pos_y - SPHERE_RADIUS <= 0:
            pos_y = SPHERE_RADIUS
            vel_y = -vel_y
        if pos_y + SPHERE_RADIUS >= TABLE_WIDTH:
            pos_y = TABLE_WIDTH - SPHERE_RADIUS
            vel_y = -vel_y
        
        #write variables back
        vel[2 * i] = vel_x
        vel[2 * i + 1] = vel_y
        pos[2 * i] = pos_x
        pos[2 * i + 1] = pos_y

@njit(cache=True)
def record_sphere_collisions_within_group(
    pos: np.ndarray, 
    collision_indices: np.ndarray,
    obj_count: int) -> int:
    """
        record any collisions within members of the group,
        based on sphere collision masks

        Parameters:
            pos: array holding positions of existing objects
            collision_indices: indices of objects in collision pairs
            obj_count: number of objects currently existing
        
        Returns:
            The number of collision pairs
    """

    collision_grid_columns = int(TABLE_LENGTH/COLLISION_BOX_SIZE)
    collision_grid_rows = int(TABLE_WIDTH/COLLISION_BOX_SIZE)
    objects_in_box = np.zeros(
        shape = (collision_grid_rows, collision_grid_columns), 
        dtype = np.int64
    )
    object_indices_in_box = np.zeros(
        shape = (collision_grid_rows, collision_grid_columns, 4 * obj_count), 
        dtype = np.int64
    )
    collision_count = 0

    for i in range(obj_count):

        #throw sphere into box(es)
        left_column = int((pos[2 * i] - SPHERE_RADIUS)/COLLISION_BOX_SIZE)
        right_column = int((pos[2 * i] + SPHERE_RADIUS)/COLLISION_BOX_SIZE)
        top_row = int((pos[2 * i + 1] - SPHERE_RADIUS)/COLLISION_BOX_SIZE)
        bottom_row = int((pos[2 * i + 1] + SPHERE_RADIUS)/COLLISION_BOX_SIZE)
        #top left
        index = objects_in_box[top_row][left_column]
        object_indices_in_box[top_row][left_column][index] = i
        objects_in_box[top_row][left_column] += 1
        #top right
        index = objects_in_box[top_row][right_column]
        object_indices_in_box[top_row][right_column][index] = i
        objects_in_box[top_row][right_column] += 1
        #bottom left
        index = objects_in_box[bottom_row][left_column]
        object_indices_in_box[bottom_row][left_column][index] = i
        objects_in_box[bottom_row][left_column] += 1
        #bottom right
        index = objects_in_box[bottom_row][right_column]
        object_indices_in_box[bottom_row][right_column][index] = i
        objects_in_box[bottom_row][right_column] += 1
        

    #check for collisions within each box
    for row in range(collision_grid_rows):
        for column in range(collision_grid_columns):
            for j in range(objects_in_box[row][column]):
                index_a = object_indices_in_box[row][column][j]
                x_a = pos[2 * index_a]
                y_a = pos[2 * index_a + 1]
                for k in range(j + 1,objects_in_box[row][column]):
                    index_b = object_indices_in_box[row][column][k]
                    if index_a == index_b:
                        continue
                    x_b = pos[2 * index_b]
                    y_b = pos[2 * index_b + 1]
                    dist = np.sqrt((x_a - x_b) ** 2 + (y_a - y_b) ** 2)
                    if dist <= 2 * SPHERE_RADIUS:

                        unique = True
                        for test_index in range(collision_count):

                            if (collision_indices[2 * test_index] == index_a)\
                                and (collision_indices[2 * test_index + 1] == index_b):
                                unique = False
                                break

                        if unique:
                            collision_indices[2 * collision_count] = index_a
                            collision_indices[2 * collision_count + 1] = index_b
                            collision_count += 1
    
    return collision_count

@njit(cache=True)
def record_sphere_collisions_brute_force(
    pos: np.ndarray,
    collision_indices: np.ndarray,
    obj_count: int) -> int:
    """
        record any collisions within members of the group,
        based on sphere collision masks.
        For smaller object counts a brute force algorithm may be
        acceptable.

        Parameters:
            pos: array holding positions of existing objects
            collision_indices: indices of objects in collision pairs
            obj_count: number of objects currently existing
        
        Returns:
            The number of collision pairs
    """

    collision_count = 0
    
    for index_a in range(obj_count):
        x_a = pos[2 * index_a]
        y_a = pos[2 * index_a + 1]
        for index_b in range(index_a + 1, obj_count):
            x_b = pos[2 * index_b]
            y_b = pos[2 * index_b + 1]
            dist = np.sqrt((x_a - x_b) ** 2 + (y_a - y_b) ** 2)
                    
            if dist <= 2 * SPHERE_RADIUS:
                collision_indices[2 * collision_count] = index_a
                collision_indices[2 * collision_count + 1] = index_b
                collision_count += 1
    
    return collision_count

@njit(cache=True)
def project_u_on_v(
    u: np.ndarray,
    v: np.ndarray,
    w: np.ndarray) -> None:
    """
        Populate w with the projection of u onto v
    """
    u_dot_v = u[0] * v[0] + u[1] * v[1] + u[2] * v[2]
    v_dot_v = v[0] * v[0] + v[1] * v[1] + v[2] * v[2]

    w[0] = v[0] * u_dot_v / v_dot_v
    w[1] = v[1] * u_dot_v / v_dot_v
    w[2] = v[2] * u_dot_v / v_dot_v

@njit(cache=True)
def resolve_sphere_collisions(
    pos: np.ndarray,
    vel: np.ndarray,
    collision_indices: np.ndarray,
    collision_count: int) -> None:
    """
        Resolve the collision pairs.

        Parameters:

            pos: array of all the sphere positions

            vel: array of all the sphere velocities

            collision_indices: array of indices of all collision pairs

            collision_count: number of collision pairs
    """

    for i in range(collision_count):

        #fetch data
        x_a = pos[2 * collision_indices[2 * i]]
        y_a = pos[2 * collision_indices[2 * i] + 1]
        x_b = pos[2 * collision_indices[2 * i + 1]]
        y_b = pos[2 * collision_indices[2 * i + 1] + 1]
        vx_a = vel[2 * collision_indices[2 * i]]
        vy_a = vel[2 * collision_indices[2 * i] + 1]
        vx_b = vel[2 * collision_indices[2 * i + 1]]
        vy_b = vel[2 * collision_indices[2 * i + 1] + 1]

        disp_a_to_b = np.array([x_b - x_a, y_b - y_a, 0.0], dtype=np.float32)
        vel_a = np.array([vx_a, vy_a, 0.0], dtype=np.float32)
        vel_b = np.array([vx_b, vy_b, 0.0], dtype=np.float32)
        temp_result = np.zeros(3, np.float32)

        #calculate new velocities
        new_vx_a = vx_a
        new_vy_a = vy_a
        project_u_on_v(u = vel_b, v = disp_a_to_b, w = temp_result)
        new_vx_a += temp_result[0]
        new_vy_a += temp_result[1]
        project_u_on_v(u = vel_a, v = -disp_a_to_b, w = temp_result)
        new_vx_a -= temp_result[0]
        new_vy_a -= temp_result[1]

        new_vx_b = vx_b
        new_vy_b = vy_b
        project_u_on_v(u = vel_a, v = disp_a_to_b, w = temp_result)
        new_vx_b += temp_result[0]
        new_vy_b += temp_result[1]
        project_u_on_v(u = vel_b, v = -disp_a_to_b, w = temp_result)
        new_vx_b -= temp_result[0]
        new_vy_b -= temp_result[1]

        #set data
        vel[2 * collision_indices[2 * i]] = new_vx_a
        vel[2 * collision_indices[2 * i] + 1] = new_vy_a
        vel[2 * collision_indices[2 * i + 1]] = new_vx_b
        vel[2 * collision_indices[2 * i + 1] + 1] = new_vy_b
        collision_indices[2 * i] = -1
        collision_indices[2 * i + 1] = -1

@njit(cache=True)
def record_sphere_collisions_two_groups_brute_force(
    pos_a: np.ndarray,
    pos_b: np.ndarray,
    collision_indices: np.ndarray,
    radius_a: float,
    radius_b: float,
    obj_count_a: int,
    obj_count_b: int) -> int:
    """
        record any collisions between members of two groups,
        based on sphere collision masks.
        For smaller object counts a brute force algorithm may be
        acceptable.

        Parameters:
            pos_a: array holding positions of group a objects
            pos_b: array holding positions of group b objects
            collision_indices: indices of objects in collision pairs
            radius_a: radius of objects in group a
            radius_b: radius of objects in group b
            obj_count_a: number of group a objects
            obj_count_b: number of group b objects
        
        Returns:
            The number of collision pairs
    """

    collision_count = 0
    
    for index_a in range(obj_count_a):
        x_a = pos_a[2 * index_a]
        y_a = pos_a[2 * index_a + 1]
        for index_b in range(obj_count_b):
            x_b = pos_b[2 * index_b]
            y_b = pos_b[2 * index_b + 1]
            dist = np.sqrt((x_a - x_b) ** 2 + (y_a - y_b) ** 2)
                    
            if dist <= radius_a + radius_b:
                collision_indices[2 * collision_count] = index_a
                collision_indices[2 * collision_count + 1] = index_b
                collision_count += 1
    
    return collision_count

@njit(cache=True)
def finalize_model_transforms(
    model_transform: np.ndarray,
    pos: np.ndarray,
    offset: int,
    obj_count: int) -> None:
    """
        Record the appropriate model transforms based on the
        given data.

        Parameters:
            model_transform: Array to hold transform matrices

            pos: array of positions for objects

            offset: index of group member to start from

            obj_count: number of group members to record
    """

    for i in range(offset, offset + obj_count):

        x = pos[2 * i]
        y = pos[2 * i + 1]
        z = 0.0

        model_matrix = np.array(
            [
                1.0, 0.0, 0.0, 0.0,
                0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                x,   y,   z,   1.0
            ],
            dtype = np.float32
        )
        
        model_transform[16 * (i - offset):16 * (i - offset + 1)] = model_matrix
    
def print_data(
    sphere_count: int, 
    pos: np.ndarray,
    vel: np.ndarray):
    
    print(f"Data holds {sphere_count} spheres")
    print(f"positions: {pos}")
    print(f"velocities: {vel}")

def time_sphere_add():

    x = np.array([100 * i for i in range(1,11)])
    y = np.zeros_like(x, dtype=np.float32)
    for j in range(x.size):
        max_spheres = int(x[j])
        print(f"Adding {max_spheres} spheres.")
        for _ in range(100):
            sphere_position = np.full(2 * max_spheres, np.nan, dtype=np.float32)
            sphere_velocity = np.full(2 * max_spheres, np.nan, dtype=np.float32)
            sphere_count = 0

            start = time.time()
            for i in range(max_spheres):
        
                sphere_count = add_dynamic_object(
                    new_x = i, new_y = 2 * i, 
                    pos = sphere_position, 
                    vel = sphere_velocity,
                    obj_count = sphere_count, max_obj_count = max_spheres
                )
    
            finish = time.time()
            y[j] += 0.01 * (finish - start) * 1000
    
    print(y)
    figure, axis = pyplot.subplots()
    axis.plot(x,y)
    figure.tight_layout()
    pyplot.show()

def test_sphere_add():

    max_spheres = 10
    sphere_position = np.full(2 * max_spheres, np.nan, dtype=np.float32)
    sphere_velocity = np.full(2 * max_spheres, np.nan, dtype=np.float32)
    sphere_count = 0

    print_data(
        sphere_count, sphere_position, sphere_velocity
    )

    for i in range(20):

        print("Add sphere")
        
        sphere_count = add_dynamic_object(
            new_x = i, new_y = 2 * i, 
            pos = sphere_position,
            vel = sphere_velocity,
            obj_count = sphere_count, max_obj_count = max_spheres
        )

        print_data(
            sphere_count, sphere_position, sphere_velocity
        )

def time_sphere_remove():

    x = np.array([100 * i for i in range(1,11)])
    y = np.zeros_like(x,dtype=np.float32)
    for j in range(x.size):
        max_spheres = int(x[j])
        print(f"Deleting {max_spheres} spheres.")
        for _ in range(100):
            sphere_position = np.full(2 * max_spheres, np.nan, dtype=np.float32)
            sphere_velocity = np.full(2 * max_spheres, np.nan, dtype=np.float32)
            sphere_count = 0

            for i in range(max_spheres):
        
                sphere_count = add_dynamic_object(
                    new_x = i, new_y = 2 * i, 
                    pos = sphere_position, 
                    vel = sphere_velocity,
                    obj_count = sphere_count, max_obj_count = max_spheres
                )

            start = time.time()
            while sphere_count > 1:

                index_to_remove = np.random.randint(1, sphere_count)

                sphere_count = remove_dynamic_object(
                    index = index_to_remove, 
                    pos = sphere_position,
                    vel = sphere_velocity,
                    obj_count = sphere_count
                )
    
            finish = time.time()
            y[j] += 0.01 * (finish - start) * 1000
    print(y)
    figure, axis = pyplot.subplots()
    axis.plot(x,y)
    figure.tight_layout()
    pyplot.show()

def test_sphere_remove():

    max_spheres = 10
    sphere_position = np.full(2 * max_spheres, np.nan, dtype=np.float32)
    sphere_velocity = np.full(2 * max_spheres, np.nan, dtype=np.float32)
    sphere_count = 0

    for i in range(10):
        
        sphere_count = add_dynamic_object(
            new_x = i, new_y = 2 * i, 
            pos = sphere_position,
            vel = sphere_velocity,
            obj_count = sphere_count, max_obj_count = max_spheres
        )
    
    while sphere_count > 1:

        index_to_remove = np.random.randint(0, 20)

        print(f"Remove sphere at index {index_to_remove}")

        sphere_count = remove_dynamic_object(
            index=index_to_remove, 
            pos = sphere_position,
            vel = sphere_velocity,
            obj_count = sphere_count
        )

        print_data(
            sphere_count, sphere_position, sphere_velocity
        )

def time_sphere_update():

    x = np.array([100 * i for i in range(1,11)])
    y = np.zeros_like(x,dtype=np.float32)
    for j in range(x.size):
        max_spheres = int(x[j])
        print(f"Updating {max_spheres} spheres.")
        for _ in range(100):

            sphere_position = np.array(
                [
                    np.random.uniform(low=SPHERE_RADIUS, high=TABLE_LENGTH - SPHERE_RADIUS)
                    for _ in range(2 * max_spheres)
                ], dtype=np.float32)
            sphere_velocity = np.array(
                [
                    np.random.uniform(low=-1.0, high=1.0)
                    for _ in range(2 * max_spheres)
                ], dtype=np.float32
            )
            sphere_count = max_spheres

            start = time.time()
            
            update_dynamic_objects(
                dt=1.0, 
                pos=sphere_position,
                vel = sphere_velocity,
                obj_count = sphere_count
            )
    
            finish = time.time()
            y[j] += 0.01 * (finish - start) * 1000
    print(y)
    figure, axis = pyplot.subplots()
    axis.plot(x,y)
    figure.tight_layout()
    pyplot.show()

def test_sphere_movement():
    
    max_spheres = 5
    sphere_position = np.array(
        [
            0.2 * i
            for i in range(2 * max_spheres)
        ], dtype=np.float32
    )
    sphere_velocity = np.array(
        [
            np.random.uniform(low=-1.0, high=1.0)
            for _ in range(2 * max_spheres)
        ], dtype=np.float32
    )
    sphere_count = max_spheres

    print_data(
        sphere_count, sphere_position, sphere_velocity
    )

    update_dynamic_objects(
        dt=1.0, 
        pos = sphere_position,
        vel = sphere_velocity,
        obj_count = sphere_count
    )
    
    print_data(
        sphere_count, sphere_position, sphere_velocity
    )

def test_sphere_rebound():
    
    max_spheres = 4
    sphere_position = np.array(
        [
            0.1, 1.0, 1.0, 0.1, 1.0, 1.7, 3.5, 1.0
        ], dtype=np.float32
    )
    sphere_velocity = np.array(
        [
            -1.0, 0.0, 0.0, -1.0, 0.0, 1.0, 1.0, 0.0
        ], dtype=np.float32
    )
    sphere_count = max_spheres

    print_data(
        sphere_count, sphere_position, sphere_velocity
    )

    update_dynamic_objects(
        dt=1.0, 
        pos = sphere_position,
        vel = sphere_velocity,
        obj_count = sphere_count
    )
    
    print_data(
        sphere_count, sphere_position, sphere_velocity
    )

def time_sphere_collide():

    x = np.array([100 * i for i in range(1,11)])
    y = np.zeros_like(x,dtype=np.float32)
    for j in range(x.size):
        max_spheres = int(x[j])
        print(f"Collision-Checking {max_spheres} spheres.")
        for _ in range(100):

            sphere_position = np.array(
                [
                    np.random.uniform(low=SPHERE_RADIUS, high=TABLE_WIDTH - SPHERE_RADIUS)
                    for _ in range(2 * max_spheres)
                ], dtype=np.float32)
            sphere_count = max_spheres
            interaction_count = int(((max_spheres - 1) * max_spheres) / 2)
            sphere_collision_indices = np.full(2 * interaction_count, -1, dtype=np.int64)

            start = time.time()
            
            record_sphere_collisions_within_group(
                pos=sphere_position,
                collision_indices=sphere_collision_indices,
                obj_count = sphere_count
            )
    
            finish = time.time()
            y[j] += 0.01 * (finish - start) * 1000
    print(y)
    figure, axis = pyplot.subplots()
    axis.plot(x,y)
    figure.tight_layout()
    pyplot.show()

def test_sphere_collide():
    
    max_spheres = 4
    sphere_pos = np.array(
        [
            1.0, 1.0, 1.1, 1.0, 1.0, 1.7, 3.5, 1.0
        ], dtype=np.float32
    )
    sphere_velocity = np.array(
        [
            0.05, 0.0, -0.05, 0.0, 0.0, 1.0, 1.0, 0.0
        ], dtype=np.float32
    )
    sphere_count = max_spheres

    interaction_count = int(((max_spheres - 1) * max_spheres) / 2)
    sphere_collision_indices = np.full(2 * interaction_count, -1, dtype=np.int64)

    print_data(
        sphere_count, sphere_pos, sphere_velocity
    )

    update_dynamic_objects(
        dt=1.0, 
        pos=sphere_pos,
        vel = sphere_velocity,
        obj_count = sphere_count
    )

    collision_count = record_sphere_collisions_within_group(
        pos = sphere_pos,
        collision_indices = sphere_collision_indices,
        obj_count = sphere_count
    )
    
    print_data(
        sphere_count, sphere_pos, sphere_velocity
    )

    print(f"{collision_count} collision(s)")
    print(sphere_collision_indices)

def time_sphere_collide_brute_force():

    x = np.array([100 * i for i in range(1,11)])
    y = np.zeros_like(x,dtype=np.float32)
    for j in range(x.size):
        max_spheres = int(x[j])
        print(f"Collision-Checking {max_spheres} spheres.")
        for _ in range(100):

            sphere_position = np.array(
                [
                    np.random.uniform(low=SPHERE_RADIUS, high=TABLE_WIDTH - SPHERE_RADIUS)
                    for _ in range(2 * max_spheres)
                ], dtype=np.float32)
            sphere_count = max_spheres
            interaction_count = int(((max_spheres - 1) * max_spheres) / 2)
            sphere_collision_indices = np.full(2 * interaction_count, -1, dtype=np.int64)

            start = time.time()
            
            record_sphere_collisions_brute_force(
                pos=sphere_position,
                collision_indices=sphere_collision_indices,
                obj_count = sphere_count
            )
    
            finish = time.time()
            y[j] += 0.01 * (finish - start) * 1000
    print(y)
    figure, axis = pyplot.subplots()
    axis.plot(x,y)
    figure.tight_layout()
    pyplot.show()

def test_sphere_collide_brute_force():
    
    max_spheres = 4
    sphere_pos = np.array(
        [
            1.0, 1.0, 1.1, 1.0, 1.0, 1.7, 3.5, 1.0
        ], dtype=np.float32
    )
    sphere_velocity = np.array(
        [
            0.05, 0.0, -0.05, 0.0, 0.0, 1.0, 1.0, 0.0
        ], dtype=np.float32
    )
    sphere_count = max_spheres

    interaction_count = int(((max_spheres - 1) * max_spheres) / 2)
    sphere_collision_indices = np.full(2 * interaction_count, -1, dtype=np.int64)

    print_data(
        sphere_count, sphere_pos, sphere_velocity
    )

    update_dynamic_objects(
        dt=1.0, 
        pos=sphere_pos,
        vel = sphere_velocity,
        obj_count = sphere_count
    )

    collision_count = record_sphere_collisions_brute_force(
        pos = sphere_pos,
        collision_indices = sphere_collision_indices,
        obj_count = sphere_count
    )
    
    print_data(
        sphere_count, sphere_pos, sphere_velocity
    )

    print(f"{collision_count} collision(s)")
    print(sphere_collision_indices)

if __name__ == "__main__":

    test_sphere_add()
    time_sphere_add()
    test_sphere_remove()
    time_sphere_remove()
    test_sphere_movement()
    test_sphere_rebound()
    time_sphere_update()
    test_sphere_collide()
    time_sphere_collide()
    test_sphere_collide_brute_force()
    time_sphere_collide_brute_force()