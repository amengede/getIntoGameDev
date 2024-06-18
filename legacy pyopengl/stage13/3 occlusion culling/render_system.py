from config import *
import component_registry
from constants import *

class RenderSystem:

    def __init__(self, registry: component_registry.ComponentRegistry):

        self.set_up_opengl()

        self.load_textures()
        self.set_up_models()

        self.wall_commands = registry.wall_commands
        self.floor_commands = registry.floor_commands
        self.wall_mask = registry.wall_mask
        self.player_pos = registry.camera_position

        self.walls = registry.walls
        self.floors = registry.floors
        self.ray_x = registry.ray_x
        self.ray_z = registry.ray_z
        self.ray_event = registry.ray_event
        self.visited_mask = registry.visited_mask

        self.drawcalls = 0
        self.registry = registry
    
    def set_up_opengl(self) -> None:

        gluPerspective(45, 640 / 480, 0.1, 50.0)

        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)

    def set_up_models(self) -> None:
        self.vertices = np.array((
            ( 0.5, -0.5, -0.5), ( 0.5,  0.5, -0.5), #west
            (-0.5,  0.5, -0.5), (-0.5, -0.5, -0.5),

            ( 0.5, -0.5,  0.5), ( 0.5,  0.5,  0.5), #east
            (-0.5,  0.5,  0.5), (-0.5, -0.5,  0.5),
            
            (-0.5, -0.5,  0.5), (-0.5,  0.5,  0.5), #south
            (-0.5,  0.5, -0.5), (-0.5, -0.5, -0.5),

            ( 0.5, -0.5,  0.5), ( 0.5,  0.5,  0.5), #north
            ( 0.5,  0.5, -0.5), ( 0.5, -0.5, -0.5),

            ( 0.5, -0.5, -0.5), ( 0.5, -0.5,  0.5), 
            (-0.5, -0.5,  0.5), (-0.5, -0.5, -0.5),

            ( 0.5,  0.5, -0.5), ( 0.5,  0.5,  0.5), 
            (-0.5,  0.5,  0.5), (-0.5,  0.5, -0.5),), dtype=np.float32)

        self.tex_coords = np.array(((1,1), (1,0), (0,0), (0,1)), dtype=np.float32)

        self.normals = np.array((
            ( 0.0,  0.0, -1.0),
            ( 0.0,  0.0,  1.0),
            (-1.0,  0.0,  0.0),
            ( 1.0,  0.0,  0.0),
            ( 0.0,  1.0,  0.0),
            ( 0.0, -1.0,  0.0)), dtype=np.float32)

        self.wall_colors = np.array((
            (1.0, 1.0, 1.0), (0.5, 0.5, 0.5), 
            (1.0, 1.0, 1.0), (0.5, 0.5, 0.5)), dtype=np.float32)

        self.v_indices_wall = np.array((
            (0, 1,  2,  3), ( 4,  5,  6,  7), 
            (8, 9, 10, 11), (12, 13, 14, 15)), dtype = np.uint8)
        self.t_indices_wall = np.array((
            (0, 1, 2, 3), (0, 1, 2, 3), 
            (0, 1, 2, 3), (0, 1, 2, 3)), dtype = np.uint8)
        
        self.v_indices_floor = np.array((16, 17, 18, 19), dtype = np.uint8)
        self.t_indices_floor = np.array((0, 1, 2, 3), dtype = np.uint8)
        self.v_indices_ceiling = np.array((20, 21, 22, 23), dtype = np.uint8)
        self.t_indices_ceiling = np.array((0, 1, 2, 3), dtype = np.uint8)

    def reset_transform(self) -> None:

        glPopMatrix()

    def apply_transform(self, row: int, col: int) -> None:

        glPushMatrix()
        glTranslatef(row + 0.5, 0, col + 0.5)

    def load_textures(self) -> None:

        self.wall_textures = {}
        self.floor_textures = {}

        for index, filename in WALL_TEXTURE_FILENAMES.items():
            self.wall_textures[index] = self.load_texture(filename)
        
        for index, filename in FLOOR_TEXTURE_FILENAMES.items():
            self.floor_textures[index] = self.load_texture(filename)
        
    def load_texture(self, filename: str) -> int:

        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        
        image = pg.image.load(filename).convert()
        width, height = image.get_rect().size
        data = pg.image.tobytes(image, "RGBA")
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        return texture

    def update(self) -> int:

        self.drawcalls = 0
        
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glColor3f(1.0, 1.0, 1.0)

        #flush out floor and ceiling commands
        for i in range(self.registry.floor_command_count):
            self.draw_floor(self.floor_commands[i])
        
        #flush out wall commands
        for i in range(self.registry.wall_command_count):
            self.draw_wall(self.wall_commands[i])
        
        self.reset_transform()
        pg.display.flip()
        return self.drawcalls

    def update_debug(self) -> None:
        
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        
        for j in range(27):
            for i in range(18):
                element = self.walls[i][j]
                if element != 0:
                    self.draw_wall_debug(element,i,j)
                    continue
                else:
                    glColor3f(1.0, 1.0, 1.0)
                    element = self.floors[i][j]
                    if element != 0:
                        self.draw_floor_debug(element,i,j)
        self.draw_debug_stuff()
        self.reset_transform()
        pg.display.flip()

    def draw_wall(self, command: np.ndarray) -> None:

        i, j, material, mask = command
        
        glBindTexture(GL_TEXTURE_2D, self.wall_textures[material])
        self.apply_transform(i, j)

        #set up for backface culling
        pos = np.array((i, 0.0, j), dtype = np.float32)
        direction = pos - self.player_pos
        direction_mag = np.sqrt(np.dot(direction, direction))
        close = abs(direction_mag) < 0.001
        direction /= direction_mag if not close else 1.0

        for face_index in range(4):
            
            #mask culling
            if (mask & 1 << face_index) == 0:
                continue

            #backface culling
            visible = np.dot(direction, self.normals[face_index]) < 0.0
            if not (close or visible):
                continue

            glColor3fv(self.wall_colors[face_index])
            edge_table_t = self.t_indices_wall[face_index]
            edge_table_v = self.v_indices_wall[face_index]

            glBegin(GL_TRIANGLE_FAN)
            for point_index in range(4):
                t = self.tex_coords[edge_table_t[point_index]]
                glTexCoord2fv(t)
                v = self.vertices[edge_table_v[point_index]]
                glVertex3fv(v)
            glEnd()
            self.drawcalls += 1
        self.reset_transform()
    
    def draw_floor(self, command: np.ndarray) -> None:

        i, j, floor, ceiling = command

        self.apply_transform(i, j)
        
        glBindTexture(GL_TEXTURE_2D, self.floor_textures[floor])
        

        glBegin(GL_TRIANGLE_FAN)
        for point_index in range(4):
            t = self.tex_coords[self.t_indices_floor[point_index]]
            glTexCoord2fv(t)
            v = self.vertices[self.v_indices_floor[point_index]]
            glVertex3fv(v)
        glEnd()
        self.drawcalls += 1

        glBindTexture(GL_TEXTURE_2D, self.floor_textures[ceiling])

        glBegin(GL_TRIANGLE_FAN)
        for point_index in range(4):
            t = self.tex_coords[self.t_indices_ceiling[point_index]]
            glTexCoord2fv(t)
            v = self.vertices[self.v_indices_ceiling[point_index]]
            glVertex3fv(v)
        glEnd()
        self.drawcalls += 1
        self.reset_transform()
    
    def draw_wall_debug(self, element: int, row: int, col: int) -> None:
        
        glBindTexture(GL_TEXTURE_2D, self.wall_textures[element])
        self.apply_transform(row, col)

        glColor3f(0.5, 0.5, 0.5)
        if (self.visited_mask[row][col]):
            glColor3f(1.0, 1.0, 1.0)

        glBegin(GL_TRIANGLE_FAN)
        for point_index in range(4):
            t = self.tex_coords[self.t_indices_floor[point_index]]
            glTexCoord2fv(t)
            v = self.vertices[self.v_indices_floor[point_index]]
            glVertex3fv(v)
        glEnd()
        self.reset_transform()
    
    def draw_floor_debug(self, element: int, row: int, col: int) -> None:
        
        glBindTexture(GL_TEXTURE_2D, self.floor_textures[element])
        self.apply_transform(row, col)

        glColor3f(0.5, 0.5, 0.5)
        if (self.visited_mask[row][col]):
            glColor3f(1.0, 1.0, 1.0)

        glBegin(GL_TRIANGLE_FAN)
        for point_index in range(4):
            t = self.tex_coords[self.t_indices_floor[point_index]]
            glTexCoord2fv(t)
            v = self.vertices[self.v_indices_floor[point_index]]
            glVertex3fv(v)
        glEnd()
        self.reset_transform()

    def draw_debug_stuff(self) -> None:

        glDisable(GL_DEPTH_TEST)
        #glEnable(GL_POINT_SIZE)
        glLineWidth(8.0)

        for i in range(512):
            glColor3f(0.0, 1.0, 1.0)
            glBegin(GL_LINES)
            glVertex3f(self.player_pos[0], 0.0, self.player_pos[2])
            glVertex3f(self.ray_x[i], 0.0, self.ray_z[i])
            glEnd()
        
        glEnable(GL_DEPTH_TEST)
        #glDisable(GL_POINT_SIZE)
