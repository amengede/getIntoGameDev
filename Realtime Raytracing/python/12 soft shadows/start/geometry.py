import room
import door
import plane
import edge

def get_lumped_geometry_from(array):
    """
        Get a description of what planes are visible.
        1: North wall
        2: East wall
        4: South wall
        8: West wall
    """

    rows = len(array)
    cols = len(array[0])

    empty_blocks = (0, "d")

    result = [[0 for col in range(cols)] for row in range(rows)]

    for row in range(rows):
        for col in range(cols):

            #block
            if array[row][col] not in empty_blocks:
                result[row][col] = 15

                #north
                if row == 0 or array[row - 1][col] not in empty_blocks:
                    result[row][col] -= 1
                
                #east
                if col == (cols - 1) or array[row][col + 1] not in empty_blocks:
                    result[row][col] -= 2
                
                #south
                if row == (rows - 1) or array[row + 1][col] not in empty_blocks:
                    result[row][col] -= 4
                
                #west
                if col == 0 or array[row][col - 1] not in empty_blocks:
                    result[row][col] -= 8
        

    return result

def get_edges(wall_mask):

    rows = len(wall_mask)
    cols = len(wall_mask[0])
    edges = []
    id = 0

    #debugging: print mask
    """
    for row in range(rows):
        for col in range(cols):
            print(f"{wall_mask[row][col]} ", end="")
        print()
    """
    
    #North edges: 1
    building_edge = False
    _edge = None
    for row in range(rows):
        for col in range(cols):
            
            if wall_mask[row][col] & 1:
                if not building_edge:
                    building_edge = True
                    _edge = edge.Edge(id)
                    id += 1
                    _edge.point_a = (row, col)
                    _edge.type = edge.NORTH
            else:
                if building_edge:
                    building_edge = False
                    _edge.point_b = (row, col - 1)
                    edges.append(_edge)
            
        if building_edge:
            building_edge = False
            _edge.point_b = (row, cols - 1)
            edges.append(_edge)
        
    #East edges: 2
    building_edge = False
    _edge = None
    for col in range(cols):
        for row in range(rows):
            
            if wall_mask[row][col] & 2:
                if not building_edge:
                    building_edge = True
                    _edge = edge.Edge(id)
                    id += 1
                    _edge.point_a = (row, col)
                    _edge.type = edge.EAST
            else:
                if building_edge:
                    building_edge = False
                    _edge.point_b = (row - 1, col)
                    edges.append(_edge)
            
        if building_edge:
            building_edge = False
            _edge.point_b = (rows - 1, col)
            edges.append(_edge)
    
    #South: 4
    building_edge = False
    _edge = None
    for row in range(rows):
        for col in range(cols):
            
            if wall_mask[row][col] & 4:
                if not building_edge:
                    building_edge = True
                    _edge = edge.Edge(id)
                    id += 1
                    _edge.point_b = (row, col)
                    _edge.type = edge.SOUTH
            else:
                if building_edge:
                    building_edge = False
                    _edge.point_a = (row, col - 1)
                    edges.append(_edge)
            
        if building_edge:
            building_edge = False
            _edge.point_a = (row, cols - 1)
            edges.append(_edge)
        
    #West: 8
    building_edge = False
    _edge = None
    for col in range(cols):
        for row in range(rows):
            
            if wall_mask[row][col] & 8:
                if not building_edge:
                    building_edge = True
                    _edge = edge.Edge(id)
                    id += 1
                    _edge.point_b = (row, col)
                    _edge.type = edge.WEST
            else:
                if building_edge:
                    building_edge = False
                    _edge.point_a = (row - 1, col)
                    edges.append(_edge)
            
        if building_edge:
            building_edge = False
            _edge.point_a = (rows - 1, col)
            edges.append(_edge)
    
    #debugging: print set of edges
    """
    for _edge in edges:
        print(f"Edge {_edge.id}: ", end="")
        if _edge.type == edge.NORTH:
            print("North: ",end="")
        elif _edge.type == edge.EAST:
            print("East: ",end="")
        elif _edge.type == edge.SOUTH:
            print("South: ",end="")
        elif _edge.type == edge.WEST:
            print("West: ",end="")
        print(f"({_edge.point_a[0]}, {_edge.point_a[1]}) -> ({_edge.point_b[0]}, {_edge.point_b[1]})")
    """

    return edges

def make_rooms(walls, doors, rooms):
    """
        Perform Depth First search to partition the empty space
        into rooms.

        Add planes to rooms.
    """

    #list of coordinates to search.
    coordinates_to_expand = []
    #history of coordinates which have already been searched.
    expanded_coordinates = []
    empty_blocks = (0, "d")

    #get the first open block to search from
    starting_coordinate = get_new_room(walls, expanded_coordinates)

    while starting_coordinate is not None:
        #start looking in a new room
        coordinates_to_expand.append(starting_coordinate)
        #empty blocks can be 0 or "d", but doors can be expanded from both sides,
        #so remove any doors currently in history.
        for i,coordinate in enumerate(expanded_coordinates):
            row, col = coordinate
            if walls[row][col] == "d":
                expanded_coordinates.pop(i)
        newRoom = room.Room()
    
        #keep expanding empty space within the room, until done.
        while len(coordinates_to_expand) > 0:

            searched_coordinate = coordinates_to_expand.pop(0)
            if searched_coordinate in expanded_coordinates:
                #just in case the algorithm tells us to search
                #the same space twice.
                continue
            expanded_coordinates.append(searched_coordinate)
            neighbors = expand(walls, searched_coordinate, expanded_coordinates)
            
            for coordinate in neighbors:
                row,col = coordinate
                #in the next iteration, only the empty space neighbours
                #will be expanded
                if walls[row][col] in empty_blocks:

                    if coordinate not in expanded_coordinates:
                        coordinates_to_expand.append(coordinate)
                    
                    #If we're on a door then search to see if the door already exists
                    #(doors can belong to multiple rooms)
                    if walls[row][col] == "d":
                        alreadyExists = False
                        for _door in doors:
                            if coordinate == _door.coordinate:
                                alreadyExists = True
                        
                        if not alreadyExists:
                            #make a door, build the central planes,
                            #then build the external planes
                            newDoor = door.Door(coordinate)
                            make_north_wall(row, col, 7, newDoor)
                            make_east_wall(row, col, 7, newDoor)
                            make_south_wall(row, col, 7, newDoor)
                            make_west_wall(row, col, 7, newDoor)
                            make_ceiling(row, col, 7, newDoor)
                            make_floor(row, col, 7, newDoor)
                            if walls[row+1][col] not in empty_blocks:
                                #horizontal, add top and bottom
                                make_north_wall(row + 1, col, 7, newDoor)
                                make_south_wall(row - 1, col, 7, newDoor)
                            else:
                                #vertical, add left and right
                                make_east_wall(row, col - 1, 7,newDoor)
                                make_west_wall(row, col + 1, 7,newDoor)
                            
                            doors.append(newDoor)
                            newRoom.doors.append(newDoor)
                        else:
                            #a door exists, find the instance of the door, and add it to the
                            #current room
                            newDoor = get_door_by_coordinate(doors, coordinate)
                            newRoom.doors.append(newDoor)

                        
                    if coordinate not in newRoom.internalCoordinates:
                        newRoom.internalCoordinates.append(coordinate)

                elif coordinate not in newRoom.coordinates:
                    newRoom.coordinates.append(coordinate)

        #this room has been fully expanded, add it to the set
        #of rooms, then attempt to start a new room.
        rooms.append(newRoom)
        starting_coordinate = get_new_room(walls, expanded_coordinates)

def get_new_room(walls, expanded_coordinates):
    """
        Search the set of rooms and if an empty space is found
        that hasn't been searched, return that coordinate.
        Otherwise, return None
    """

    #get dimensions of map
    rows = len(walls)
    cols = len(walls[0])

    for row in range(rows):
        for col in range(cols):
            if walls[row][col] == 0:
                possible_solution = (row,col)
                if possible_solution not in expanded_coordinates:
                    return possible_solution
    return None

def expand(walls, coordinate, expanded_coordinates):
    """
        return the neighbourhood of coordinates around a given coordinate,
        returning all those which are in the same room.
    """

    coordinates = [coordinate,]

    rows = len(walls)
    cols = len(walls[0])
    
    row,col = coordinate

    onDoor = (walls[row][col] == "d")

    if row > 0:
        if (not onDoor) \
            or (onDoor and walls[row - 1][col] != 0) \
            and coordinate not in expanded_coordinates:
            coordinates.append((row - 1, col))
    if row < rows - 1:
        if (not onDoor) \
            or (onDoor and walls[row + 1][col] != 0) \
            and coordinate not in expanded_coordinates:
            coordinates.append((row + 1, col))
    if col > 0:
        if (not onDoor) \
            or (onDoor and walls[row][col - 1] != 0) \
            and coordinate not in expanded_coordinates:
            coordinates.append((row, col - 1))
    if col < cols - 1:
        if (not onDoor) \
            or (onDoor and walls[row][col + 1] != 0) \
            and coordinate not in expanded_coordinates:
            coordinates.append((row, col + 1))
    
    return coordinates

def send_edge(_edge, target):

    if _edge.convex:
        return

    if _edge.type == edge.NORTH:
        x_center = (_edge.point_a[1] + _edge.point_b[1] + 1)/2
        y_center = _edge.point_a[0]
        width = (_edge.point_b[1] + 1 - _edge.point_a[1])/2
        target.planes.append(
            plane.Plane(
                normal    = [0, -1, 0],
                tangent   = [-1, 0, 0],
                bitangent = [0, 0, -1],
                uMin = -width,
                uMax = width,
                vMin = -0.5,
                vMax = 0.5,
                center = [x_center, y_center, 0.5],
                material_index = 0
            )
        )
    elif _edge.type == edge.EAST:
        x_center = _edge.point_a[1] + 1
        y_center = (_edge.point_a[0] + _edge.point_b[0] + 1)/2
        width = (_edge.point_b[0] + 1 - _edge.point_a[0])/2
        target.planes.append(
            plane.Plane(
                normal    = [1, 0, 0],
                tangent   = [0, 1, 0],
                bitangent = [0, 0, 1],
                uMin = -width,
                uMax = width,
                vMin = -0.5,
                vMax = 0.5,
                center = [x_center, y_center, 0.5],
                material_index = 0
            )
        )
    elif _edge.type == edge.SOUTH:
        x_center = (_edge.point_a[1] + _edge.point_b[1] + 1)/2
        y_center = _edge.point_a[0] + 1
        width = (_edge.point_b[1] + 1 - _edge.point_a[1])/2
        target.planes.append(
            plane.Plane(
                normal    = [ 0, 1, 0],
                tangent   = [-1, 0, 0],
                bitangent = [ 0, 0, 1],
                uMin = -width,
                uMax = width,
                vMin = -0.5,
                vMax = 0.5,
                center = [x_center, y_center, 0.5],
                material_index = 0
            )
        )
    elif _edge.type == edge.WEST:
        x_center = _edge.point_a[1]
        y_center = (_edge.point_a[0] + _edge.point_b[0] + 1)/2
        width = (_edge.point_b[0] + 1 - _edge.point_a[0])/2
        target.planes.append(
            plane.Plane(
                normal    = [-1, 0, 0],
                tangent   = [0, 1, 0],
                bitangent = [0, 0, -1],
                uMin = -width,
                uMax = width,
                vMin = -0.5,
                vMax = 0.5,
                center = [x_center, y_center, 0.5],
                material_index = 0
            )
        )

def make_north_wall(row, col, material, target):

    #x,y,z,u,v,tx,ty,tz,bx,by,bz,nx,ny,nz
    vertices = [
        col + 1.0, row, 1.0, 1.0/5.0, (9.0 - material)/9.0,         -1.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, -1.0, 0.0, #z+,x+
        col,       row, 1.0, 0.0,     (9.0 - material)/9.0,         -1.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, -1.0, 0.0, #z+,x-
        col,       row, 0.0, 0.0,     (9.0 - (material + 1.0))/9.0, -1.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, -1.0, 0.0, #z-,x-

        col,       row, 0.0, 0.0,     (9.0 - (material + 1.0))/9.0, -1.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, -1.0, 0.0, #z-,x-
        col + 1.0, row, 0.0, 1.0/5.0, (9.0 - (material + 1.0))/9.0, -1.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, -1.0, 0.0, #z-,x+
        col + 1.0, row, 1.0, 1.0/5.0, (9.0 - material)/9.0,         -1.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, -1.0, 0.0, #z+,x+
    ]

    for data in vertices:
        target.vertices.append(data)
    
    target.vertexCount += 6
    
def make_east_wall(row, col, material, target):

    #x,y,z,u,v,tx,ty,tz,bx,by,bz,nx,ny,nz
    vertices = [
        col + 1.0, row,       0.0, 0.0,     (9.0 - (material + 1.0))/9.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, #z-,y-
        col + 1.0, row + 1.0, 0.0, 1.0/5.0, (9.0 - (material + 1.0))/9.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, #z-,y+
        col + 1.0, row + 1.0, 1.0, 1.0/5.0, (9.0 - material)/9.0,         0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, #z+,y+

        col + 1.0, row + 1.0, 1.0, 1.0/5.0, (9.0 - material)/9.0,         0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, #z+,y+
        col + 1.0, row,       1.0, 0.0,     (9.0 - material)/9.0,         0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, #z+,y-
        col + 1.0, row,       0.0, 0.0,     (9.0 - (material + 1.0))/9.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, #z-,y-
    ]

    for data in vertices:
        target.vertices.append(data)
    
    target.vertexCount += 6

def make_south_wall(row, col, material, target):

    #x,y,z,u,v,tx,ty,tz,bx,by,bz,nx,ny,nz
    vertices = [
        col + 1.0, row + 1.0, 1.0, 1.0/5.0, (9.0 - material)/9.0,         -1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, #z+,x+
        col + 1.0, row + 1.0, 0.0, 1.0/5.0, (9.0 - (material + 1.0))/9.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, #z-,x+
        col,       row + 1.0, 0.0, 0.0,     (9.0 - (material + 1.0))/9.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, #z-,x-

        col,       row + 1.0, 0.0, 0.0,     (9.0 - (material + 1.0))/9.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, #z-,x-
        col,       row + 1.0, 1.0, 0.0,     (9.0 - material)/9.0,         -1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, #z+,x-
        col + 1.0, row + 1.0, 1.0, 1.0/5.0, (9.0 - material)/9.0,         -1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, #z+,x+
    ]

    for data in vertices:
        target.vertices.append(data)
    
    target.vertexCount += 6

def make_west_wall(row, col, material, target):

    #x,y,z,u,v,tx,ty,tz,bx,by,bz,nx,ny,nz
    vertices = [
        col, row + 1.0, 1.0, 1.0/5.0, (9.0 - material)/9.0,         0.0, 1.0, 0.0, 0.0, 0.0, -1.0, -1.0, 0.0, 0.0, #z+,y+
        col, row + 1.0, 0.0, 1.0/5.0, (9.0 - (material + 1.0))/9.0, 0.0, 1.0, 0.0, 0.0, 0.0, -1.0, -1.0, 0.0, 0.0, #z-,y+
        col, row,       0.0, 0.0,     (9.0 - (material + 1.0))/9.0, 0.0, 1.0, 0.0, 0.0, 0.0, -1.0, -1.0, 0.0, 0.0, #z-,y-

        col, row,       0.0, 0.0,     (9.0 - (material + 1.0))/9.0, 0.0, 1.0, 0.0, 0.0, 0.0, -1.0, -1.0, 0.0, 0.0, #z-,y-
        col, row,       1.0, 0.0,     (9.0 - material)/9.0,         0.0, 1.0, 0.0, 0.0, 0.0, -1.0, -1.0, 0.0, 0.0, #z+,y-
        col, row + 1.0, 1.0, 1.0/5.0, (9.0 - material)/9.0,         0.0, 1.0, 0.0, 0.0, 0.0, -1.0, -1.0, 0.0, 0.0, #z+,y+
    ]

    for data in vertices:
        target.vertices.append(data)
    
    target.vertexCount += 6

def make_ceiling(row, col, material, target):

    #x,y,z,u,v,tx,ty,tz,bx,by,bz,nx,ny,nz
    vertices = [
        col + 1, row,       1.0, 1.0/5.0, (9.0 - material)/9.0,         0.0, -1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, -1.0, #x+,y-
        col,     row,       1.0, 1.0/5.0, (9.0 - (material + 1.0))/9.0, 0.0, -1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, -1.0, #x-,y-
        col,     row + 1.0, 1.0, 0.0,     (9.0 - (material + 1.0))/9.0, 0.0, -1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, -1.0, #x-,y+

        col,     row + 1.0, 1.0, 0.0,     (9.0 - (material + 1.0))/9.0, 0.0, -1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, -1.0, #x-,y+
        col + 1, row + 1.0, 1.0, 0.0,     (9.0 - material)/9.0,         0.0, -1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, -1.0, #x+,y+
        col + 1, row,       1.0, 1.0/5.0, (9.0 - material)/9.0,         0.0, -1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, -1.0, #x+,y-
    ]

    for data in vertices:
        target.vertices.append(data)
    
    target.vertexCount += 6

def make_floor(row, col, material, target):

    #x,y,z,u,v,tx,ty,tz,bx,by,bz,nx,ny,nz
    vertices = [
        col + 1.0, row + 1.0, 0.0, 1.0/5.0, (9.0 - material)/9.0,         0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0, #x+,y+
        col,       row + 1.0, 0.0, 1.0/5.0, (9.0 - (material + 1.0))/9.0, 0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0, #x-,y+
        col,       row,       0.0, 0.0,     (9.0 - (material + 1.0))/9.0, 0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0, #x-,y-

        col,       row,       0.0, 0.0,     (9.0 - (material + 1.0))/9.0, 0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0, #x-,y-
        col + 1.0, row,       0.0, 0.0,     (9.0 - material)/9.0,         0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0, #x+,y-
        col + 1.0, row + 1.0, 0.0, 1.0/5.0, (9.0 - material)/9.0,         0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0, #x+,y+
    ]

    for data in vertices:
        target.vertices.append(data)
    
    target.vertexCount += 6

def get_door_by_coordinate(doors, coordinate):

    for _door in doors:
        if _door.coordinate == coordinate:
            return _door

def get_geometry_at_point(row, col, target, walls, floors, ceilings, wall_mask):

    if wall_mask[row][col] & 1:
        make_north_wall(row, col, walls[row][col] - 1, target)
                
    if wall_mask[row][col] & 2:
        make_east_wall(row, col, walls[row][col] - 1, target)
                
    if wall_mask[row][col] & 4:
        make_south_wall(row, col, walls[row][col] - 1, target)

    if wall_mask[row][col] & 8:
        make_west_wall(row, col, walls[row][col] - 1, target)
    
    if walls[row][col] == 0:
        make_floor(row, col, floors[row][col] - 1, target)
        make_ceiling(row, col, ceilings[row][col] - 1, target)

def classify_edges(edges):

    for _edge in edges:

        if _edge.convex is not None:
            continue

        for _edge2 in edges:

            if _edge2 == _edge:
                continue

            row_check = abs(_edge.point_b[0] - _edge2.point_a[0]) <= 1
            col_check = abs(_edge.point_b[1] - _edge2.point_a[1]) <= 1

            if row_check and col_check:
                convex = is_convex(_edge.type, _edge2.type)

                if _edge.convex is None:
                    _edge.convex = convex
                else:
                    _edge.convex = _edge.convex and convex

                if _edge2.convex is None:
                    _edge2.convex = convex
                else:
                    _edge2.convex = _edge2.convex and convex
                #print(f"Edge {_edge.id} connects to edge {_edge2.id}")
                #print(f"convex: {convex}")
                break

def is_convex(type_1, type_2):

    if type_1 == edge.NORTH:
        return type_2 == edge.WEST
    
    if type_1 == edge.WEST:
        return type_2 == edge.SOUTH
    
    if type_1 == edge.SOUTH:
        return type_2 == edge.EAST
    
    if type_1 == edge.EAST:
        return type_2 == edge.NORTH