from config import *

@njit(cache=True)
def add_dynamic_object(
    new_x: float, new_y: float, 
    pos_x: np.ndarray, pos_y: np.ndarray, 
    vel_x: np.ndarray, vel_y: np.ndarray, 
    obj_count: int, max_obj_count: int) -> int:
    """
        Try to record a new dynamic object (position and velocity)

        Parameters:
            new_x: x coordinate of the object to be added
            new_y: y coordinate of the object to be added
            pos_x: array holding x coordinates of objects
            pos_y: array holding y coordinates of objects
            vel_x: array holding x velocity components of objects
            vel_y: array holding y velocity components of objects
            obj_count: number of objects currently existing
            max_obj_count: maximum capacity of arrays
        
        Returns:
            The number of current objects after adding
    """
    
    if obj_count == max_obj_count:
        return obj_count
    
    pos_x[obj_count] = new_x
    pos_y[obj_count] = new_y
    vel_x[obj_count] = 0.0
    vel_y[obj_count] = 0.0
    
    return obj_count + 1

@njit(cache=True)
def remove_dynamic_object(
    index: int, 
    pos_x: np.ndarray, pos_y: np.ndarray, 
    vel_x: np.ndarray, vel_y: np.ndarray, 
    obj_count: int) -> int:
    """
        Try to remove a dynamic object (position and velocity)

        Parameters:
            index: index of the sphere to remove
            pos_x: array holding x coordinates of existing objects
            pos_y: array holding y coordinates of existing objects
            vel_x: array holding x velocity components of existing objects
            vel_y: array holding y velocity components of existing objects
            obj_count: number of objects currently existing
        
        Returns:
            The number of current objects after removal
    """

    if index <= 0 or index >= obj_count:
        return obj_count
    
    for i in range(index, obj_count - 1):
    
        pos_x[i] = pos_x[i + 1]
        pos_y[i] = pos_y[i + 1]
        vel_x[i] = vel_x[i + 1]
        vel_y[i] = vel_y[i + 1]
    
    pos_x[obj_count - 1] = np.nan
    pos_y[obj_count - 1] = np.nan
    vel_x[obj_count - 1] = np.nan
    vel_y[obj_count - 1] = np.nan
    
    return obj_count - 1

@njit(cache=True)
def update_dynamic_objects(
    dt: float, 
    pos_x: np.ndarray, pos_y: np.ndarray, 
    vel_x: np.ndarray, vel_y: np.ndarray, 
    obj_count: int) -> None:
    """
        Update dynamic objects

        Parameters:
            dt: number of seconds since last update
            pos_x: array holding x coordinates of existing objects
            pos_y: array holding y coordinates of existing objects
            vel_x: array holding x velocity components of existing objects
            vel_y: array holding y velocity components of existing objects
            obj_count: number of objects currently existing
    """

    for i in range(obj_count):

        #apply friction to velocities
        vel_x[i] = TABLE_FRICTION_MULTIPLIER * vel_x[i]
        if np.abs(vel_x[i]) < 1e-7:
            vel_x[i] = 0.0
        vel_y[i] = TABLE_FRICTION_MULTIPLIER * vel_y[i]
        if np.abs(vel_y[i]) < 1e-7:
            vel_y[i] = 0.0

        #update positions, check boundary conditions
        pos_x[i] = pos_x[i] + dt * vel_x[i]
        if pos_x[i] - SPHERE_RADIUS <= 0:
            pos_x[i] = SPHERE_RADIUS
            vel_x[i] = -vel_x[i]
        if pos_x[i] + SPHERE_RADIUS >= TABLE_LENGTH:
            pos_x[i] = TABLE_LENGTH - SPHERE_RADIUS
            vel_x[i] = -vel_x[i]
        
        pos_y[i] = pos_y[i] + dt * vel_y[i]
        if pos_y[i] - SPHERE_RADIUS <= 0:
            pos_y[i] = SPHERE_RADIUS
            vel_y[i] = -vel_y[i]
        if pos_y[i] + SPHERE_RADIUS >= TABLE_WIDTH:
            pos_y[i] = TABLE_WIDTH - SPHERE_RADIUS
            vel_y[i] = -vel_y[i]

@njit(cache=True)
def record_sphere_collisions_within_group(
    pos_x: np.ndarray, pos_y: np.ndarray, 
    collision_indices_a: np.ndarray, collision_indices_b: np.ndarray,
    obj_count: int) -> int:
    """
        record any collisions within members of the group,
        based on sphere collision masks

        Parameters:
            pos_x: array holding x coordinates of existing objects
            pos_y: array holding y coordinates of existing objects
            collision_indices_a: indices of first objects in collision pairs
            collision_indices_b: indices of first objects in collision pairs
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
        left_column = int((pos_x[i] - SPHERE_RADIUS)/COLLISION_BOX_SIZE)
        right_column = int((pos_x[i] + SPHERE_RADIUS)/COLLISION_BOX_SIZE)
        top_row = int((pos_y[i] - SPHERE_RADIUS)/COLLISION_BOX_SIZE)
        bottom_row = int((pos_y[i] + SPHERE_RADIUS)/COLLISION_BOX_SIZE)
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
                for k in range(j + 1,objects_in_box[row][column]):
                    index_b = object_indices_in_box[row][column][k]
                    if index_a == index_b:
                        continue
                    x_a = pos_x[index_a]
                    y_a = pos_y[index_a]
                    x_b = pos_x[index_b]
                    y_b = pos_y[index_b]
                    dist = np.sqrt((x_a - x_b) ** 2 + (y_a - y_b) ** 2)
                    if dist <= 2 * SPHERE_RADIUS:

                        unique = True
                        for test_index in range(collision_count):

                            if (collision_indices_a[test_index] == index_a)\
                                and (collision_indices_b[test_index] == index_b):
                                unique = False
                                break

                        if unique:
                            collision_indices_a[collision_count] = index_a
                            collision_indices_b[collision_count] = index_b
                            collision_count += 1
    
    return collision_count

@njit(cache=True)
def record_sphere_collisions_brute_force(
    pos_x: np.ndarray, pos_y: np.ndarray, 
    collision_indices_a: np.ndarray, collision_indices_b: np.ndarray,
    obj_count: int) -> int:
    """
        record any collisions within members of the group,
        based on sphere collision masks.
        For smaller object counts a brute force algorithm may be
        acceptable.

        Parameters:
            pos_x: array holding x coordinates of existing objects
            pos_y: array holding y coordinates of existing objects
            collision_indices_a: indices of first objects in collision pairs
            collision_indices_b: indices of first objects in collision pairs
            obj_count: number of objects currently existing
        
        Returns:
            The number of collision pairs
    """

    collision_count = 0
    
    for index_a in range(obj_count):
        for index_b in range(index_a + 1, obj_count):
                    
            x_a = pos_x[index_a]
            y_a = pos_y[index_a]
            x_b = pos_x[index_b]
            y_b = pos_y[index_b]
            dist = np.sqrt((x_a - x_b) ** 2 + (y_a - y_b) ** 2)
                    
            if dist <= 2 * SPHERE_RADIUS:
                collision_indices_a[collision_count] = index_a
                collision_indices_b[collision_count] = index_b
                collision_count += 1
    
    return collision_count

def print_data(
    sphere_count: int, 
    pos_x: np.ndarray, pos_y: np.ndarray, 
    vel_x: np.ndarray, vel_y: np.ndarray):
    
    print(f"Data holds {sphere_count} spheres")
    print(f"x data: {pos_x}")
    print(f"y data: {pos_y}")
    print(f"v_x data: {vel_x}")
    print(f"v_y data: {vel_y}")

def time_sphere_add():

    x = np.array([10 ** i for i in range(1,5)])
    y = np.zeros_like(x, dtype=np.float32)
    for j in range(x.size):
        max_spheres = int(x[j])
        print(f"Adding {max_spheres} spheres.")
        for _ in range(100):
            sphere_x = np.full(max_spheres, np.nan, dtype=np.float32)
            sphere_y = np.full(max_spheres, np.nan, dtype=np.float32)
            sphere_velocity_x = np.full(max_spheres, np.nan, dtype=np.float32)
            sphere_velocity_y = np.full(max_spheres, np.nan, dtype=np.float32)
            sphere_count = 0

            start = time.time()
            for i in range(max_spheres):
        
                sphere_count = add_dynamic_object(
                    new_x = i, new_y = 2 * i, 
                    pos_x = sphere_x, pos_y = sphere_y, 
                    vel_x = sphere_velocity_x, vel_y = sphere_velocity_y,
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
    sphere_x = np.full(max_spheres, np.nan, dtype=np.float32)
    sphere_y = np.full(max_spheres, np.nan, dtype=np.float32)
    sphere_velocity_x = np.full(max_spheres, np.nan, dtype=np.float32)
    sphere_velocity_y = np.full(max_spheres, np.nan, dtype=np.float32)
    sphere_count = 0

    print_data(
        sphere_count, sphere_x, sphere_y, sphere_velocity_x, sphere_velocity_y
    )

    for i in range(20):

        print("Add sphere")
        
        sphere_count = add_dynamic_object(
            new_x = i, new_y = 2 * i, 
            pos_x = sphere_x, pos_y = sphere_y, 
            vel_x = sphere_velocity_x, vel_y = sphere_velocity_y,
            obj_count = sphere_count, max_obj_count = max_spheres
        )

        print_data(
            sphere_count, sphere_x, sphere_y, sphere_velocity_x, sphere_velocity_y
        )

def time_sphere_remove():

    x = np.array([10 ** i for i in range(1,5)])
    y = np.zeros_like(x,dtype=np.float32)
    for j in range(x.size):
        max_spheres = int(x[j])
        print(f"Deleting {max_spheres} spheres.")
        for _ in range(100):
            sphere_x = np.full(max_spheres, np.nan, dtype=np.float32)
            sphere_y = np.full(max_spheres, np.nan, dtype=np.float32)
            sphere_velocity_x = np.full(max_spheres, np.nan, dtype=np.float32)
            sphere_velocity_y = np.full(max_spheres, np.nan, dtype=np.float32)
            sphere_count = 0

            for i in range(max_spheres):
        
                sphere_count = add_dynamic_object(
                    new_x = i, new_y = 2 * i, 
                    pos_x = sphere_x, pos_y = sphere_y, 
                    vel_x = sphere_velocity_x, vel_y = sphere_velocity_y,
                    obj_count = sphere_count, max_obj_count = max_spheres
                )

            start = time.time()
            while sphere_count > 1:

                index_to_remove = np.random.randint(1, sphere_count)

                sphere_count = remove_dynamic_object(
                    index=index_to_remove, 
                    pos_x=sphere_x, pos_y=sphere_y,
                    vel_x = sphere_velocity_x, vel_y = sphere_velocity_y,
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
    sphere_x = np.full(max_spheres, np.nan, dtype=np.float32)
    sphere_y = np.full(max_spheres, np.nan, dtype=np.float32)
    sphere_velocity_x = np.full(max_spheres, np.nan, dtype=np.float32)
    sphere_velocity_y = np.full(max_spheres, np.nan, dtype=np.float32)
    sphere_count = 0

    for i in range(10):
        
        sphere_count = add_dynamic_object(
            new_x = i, new_y = 2 * i, 
            pos_x = sphere_x, pos_y = sphere_y, 
            vel_x = sphere_velocity_x, vel_y = sphere_velocity_y,
            obj_count = sphere_count, max_obj_count = max_spheres
        )
    
    while sphere_count > 1:

        index_to_remove = np.random.randint(0, 20)

        print(f"Remove sphere at index {index_to_remove}")

        sphere_count = remove_dynamic_object(
            index=index_to_remove, 
            pos_x=sphere_x, pos_y=sphere_y,
            vel_x = sphere_velocity_x, vel_y = sphere_velocity_y,
            obj_count = sphere_count
        )

        print_data(
            sphere_count, sphere_x, sphere_y, sphere_velocity_x, sphere_velocity_y
        )

def time_sphere_update():

    x = np.array([10 ** i for i in range(1,5)])
    y = np.zeros_like(x,dtype=np.float32)
    for j in range(x.size):
        max_spheres = int(x[j])
        print(f"Updating {max_spheres} spheres.")
        for _ in range(100):

            sphere_x = np.array(
                [
                    np.random.uniform(low=SPHERE_RADIUS, high=TABLE_LENGTH - SPHERE_RADIUS)
                    for _ in range(max_spheres)
                ], dtype=np.float32
            )
            sphere_y = np.array(
                [
                    np.random.uniform(low=SPHERE_RADIUS, high=TABLE_WIDTH - SPHERE_RADIUS)
                    for _ in range(max_spheres)
                ], dtype=np.float32
            )
            sphere_velocity_x = np.array(
                [
                    np.random.uniform(low=-1.0, high=1.0)
                    for _ in range(max_spheres)
                ], dtype=np.float32
            )
            sphere_velocity_y = np.array(
                [
                    np.random.uniform(low=-1.0, high=1.0)
                    for _ in range(max_spheres)
                ], dtype=np.float32
            )
            sphere_count = max_spheres

            start = time.time()
            
            update_dynamic_objects(
                dt=1.0, 
                pos_x=sphere_x, pos_y=sphere_y,
                vel_x = sphere_velocity_x, vel_y = sphere_velocity_y,
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
    sphere_x = np.array(
        [
            0.2 * i
            for i in range(max_spheres)
        ], dtype=np.float32
    )
    sphere_y = np.array(
        [
            0.2 * i
            for i in range(max_spheres)
        ], dtype=np.float32
    )
    sphere_velocity_x = np.array(
        [
            np.random.uniform(low=-1.0, high=1.0)
            for _ in range(max_spheres)
        ], dtype=np.float32
    )
    sphere_velocity_y = np.array(
        [
            np.random.uniform(low=-1.0, high=1.0)
            for _ in range(max_spheres)
        ], dtype=np.float32
    )
    sphere_count = max_spheres

    print_data(
        sphere_count, sphere_x, sphere_y, sphere_velocity_x, sphere_velocity_y
    )

    update_dynamic_objects(
        dt=1.0, 
        pos_x=sphere_x, pos_y=sphere_y,
        vel_x = sphere_velocity_x, vel_y = sphere_velocity_y,
        obj_count = sphere_count
    )
    
    print_data(
        sphere_count, sphere_x, sphere_y, sphere_velocity_x, sphere_velocity_y
    )

def test_sphere_rebound():
    
    max_spheres = 4
    sphere_x = np.array(
        [
            0.1, 1.0, 1.0, 3.5
        ], dtype=np.float32
    )
    sphere_y = np.array(
        [
            1.0, 0.1, 1.7, 1.0
        ], dtype=np.float32
    )
    sphere_velocity_x = np.array(
        [
            -1.0, 0.0, 0.0, 1.0
        ], dtype=np.float32
    )
    sphere_velocity_y = np.array(
        [
            0.0, -1.0, 1.0, 0.0
        ], dtype=np.float32
    )
    sphere_count = max_spheres

    print_data(
        sphere_count, sphere_x, sphere_y, sphere_velocity_x, sphere_velocity_y
    )

    update_dynamic_objects(
        dt=1.0, 
        pos_x=sphere_x, pos_y=sphere_y,
        vel_x = sphere_velocity_x, vel_y = sphere_velocity_y,
        obj_count = sphere_count
    )
    
    print_data(
        sphere_count, sphere_x, sphere_y, sphere_velocity_x, sphere_velocity_y
    )

def time_sphere_collide():

    x = np.array([10 ** i for i in range(1,5)])
    y = np.zeros_like(x,dtype=np.float32)
    for j in range(x.size):
        max_spheres = int(x[j])
        print(f"Collision-Checking {max_spheres} spheres.")
        for _ in range(100):

            sphere_x = np.array(
                [
                    np.random.uniform(low=SPHERE_RADIUS, high=TABLE_LENGTH - SPHERE_RADIUS)
                    for _ in range(max_spheres)
                ], dtype=np.float32
            )
            sphere_y = np.array(
                [
                    np.random.uniform(low=SPHERE_RADIUS, high=TABLE_WIDTH - SPHERE_RADIUS)
                    for _ in range(max_spheres)
                ], dtype=np.float32
            )
            sphere_count = max_spheres
            interaction_count = int(((max_spheres - 1) * max_spheres) / 2)
            sphere_collision_indices_a = np.full(interaction_count, -1, dtype=np.int64)
            sphere_collision_indices_b = np.full(interaction_count, -1, dtype=np.int64)

            start = time.time()
            
            record_sphere_collisions_within_group(
                pos_x=sphere_x, pos_y=sphere_y,
                collision_indices_a = sphere_collision_indices_a,
                collision_indices_b = sphere_collision_indices_b,
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
    sphere_x = np.array(
        [
            1.0, 1.1, 1.0, 3.5
        ], dtype=np.float32
    )
    sphere_y = np.array(
        [
            1.0, 1.0, 1.7, 1.0
        ], dtype=np.float32
    )
    sphere_velocity_x = np.array(
        [
            0.05, -0.05, 0.0, 1.0
        ], dtype=np.float32
    )
    sphere_velocity_y = np.array(
        [
            0.0, 0.0, 1.0, 0.0
        ], dtype=np.float32
    )
    sphere_count = max_spheres

    interaction_count = int(((max_spheres - 1) * max_spheres) / 2)
    sphere_collision_indices_a = np.full(interaction_count, -1, dtype=np.int64)
    sphere_collision_indices_b = np.full(interaction_count, -1, dtype=np.int64)

    print_data(
        sphere_count, sphere_x, sphere_y, sphere_velocity_x, sphere_velocity_y
    )

    update_dynamic_objects(
        dt=1.0, 
        pos_x=sphere_x, pos_y=sphere_y,
        vel_x = sphere_velocity_x, vel_y = sphere_velocity_y,
        obj_count = sphere_count
    )

    collision_count = record_sphere_collisions_within_group(
        pos_x = sphere_x, pos_y = sphere_y,
        collision_indices_a = sphere_collision_indices_a,
        collision_indices_b = sphere_collision_indices_b,
        obj_count = sphere_count
    )
    
    print_data(
        sphere_count, sphere_x, sphere_y, sphere_velocity_x, sphere_velocity_y
    )

    print(f"{collision_count} collision(s)")
    print(sphere_collision_indices_a)
    print(sphere_collision_indices_b)

def time_sphere_collide_brute_force():

    x = np.array([10 ** i for i in range(1,5)])
    y = np.zeros_like(x,dtype=np.float32)
    for j in range(x.size):
        max_spheres = int(x[j])
        print(f"Collision-Checking {max_spheres} spheres.")
        for _ in range(100):

            sphere_x = np.array(
                [
                    np.random.uniform(low=SPHERE_RADIUS, high=TABLE_LENGTH - SPHERE_RADIUS)
                    for _ in range(max_spheres)
                ], dtype=np.float32
            )
            sphere_y = np.array(
                [
                    np.random.uniform(low=SPHERE_RADIUS, high=TABLE_WIDTH - SPHERE_RADIUS)
                    for _ in range(max_spheres)
                ], dtype=np.float32
            )
            sphere_count = max_spheres
            interaction_count = int(((max_spheres - 1) * max_spheres) / 2)
            sphere_collision_indices_a = np.full(interaction_count, -1, dtype=np.int64)
            sphere_collision_indices_b = np.full(interaction_count, -1, dtype=np.int64)

            start = time.time()
            
            record_sphere_collisions_brute_force(
                pos_x=sphere_x, pos_y=sphere_y,
                collision_indices_a = sphere_collision_indices_a,
                collision_indices_b = sphere_collision_indices_b,
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
    sphere_x = np.array(
        [
            1.0, 1.1, 1.0, 3.5
        ], dtype=np.float32
    )
    sphere_y = np.array(
        [
            1.0, 1.0, 1.7, 1.0
        ], dtype=np.float32
    )
    sphere_velocity_x = np.array(
        [
            0.05, -0.05, 0.0, 1.0
        ], dtype=np.float32
    )
    sphere_velocity_y = np.array(
        [
            0.0, 0.0, 1.0, 0.0
        ], dtype=np.float32
    )
    sphere_count = max_spheres

    interaction_count = int(((max_spheres - 1) * max_spheres) / 2)
    sphere_collision_indices_a = np.full(interaction_count, -1, dtype=np.int64)
    sphere_collision_indices_b = np.full(interaction_count, -1, dtype=np.int64)

    print_data(
        sphere_count, sphere_x, sphere_y, sphere_velocity_x, sphere_velocity_y
    )

    update_dynamic_objects(
        dt=1.0, 
        pos_x=sphere_x, pos_y=sphere_y,
        vel_x = sphere_velocity_x, vel_y = sphere_velocity_y,
        obj_count = sphere_count
    )

    collision_count = record_sphere_collisions_brute_force(
        pos_x = sphere_x, pos_y = sphere_y,
        collision_indices_a = sphere_collision_indices_a,
        collision_indices_b = sphere_collision_indices_b,
        obj_count = sphere_count
    )
    
    print_data(
        sphere_count, sphere_x, sphere_y, sphere_velocity_x, sphere_velocity_y
    )

    print(f"{collision_count} collision(s)")
    print(sphere_collision_indices_a)
    print(sphere_collision_indices_b)

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