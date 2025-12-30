from config import *
import component_registry
from constants import *

class RenderSystem:

    def __init__(self, registry: component_registry.ComponentRegistry):

        self.set_up_opengl()

        self.load_textures()
        self.set_up_models()

        self.floors = registry.floors
        self.walls = registry.walls
        self.ceilings = registry.ceilings
        self.wall_mask = registry.wall_mask

        self.drawcalls = 0
    
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
        glTranslatef(float(row), 0, float(col))

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
        
        for j in range(27):
            for i in range(18):
                element = self.walls[i][j]
                if element != 0:
                    self.draw_wall(element,i,j, self.wall_mask[i][j])
                    continue
                else:
                    glColor3f(1.0, 1.0, 1.0)
                    element = self.floors[i][j]
                    if element != 0:
                        self.draw_floor(element,i,j)
                        self.draw_ceiling(self.ceilings[i][j],i,j)
        self.reset_transform()
        pg.display.flip()
        return self.drawcalls

    def draw_wall(self, element: int, row: int, col: int, mask: int) -> None:
        
        glBindTexture(GL_TEXTURE_2D, self.wall_textures[element])
        self.apply_transform(row, col)

        for face_index in range(4):

            #is wall masked out?
            if (mask & 1 << face_index) == 0:
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
    
    def draw_floor(self, element: int, row: int, col: int) -> None:
        
        glBindTexture(GL_TEXTURE_2D, self.floor_textures[element])
        self.apply_transform(row, col)

        glBegin(GL_TRIANGLE_FAN)
        for point_index in range(4):
            t = self.tex_coords[self.t_indices_floor[point_index]]
            glTexCoord2fv(t)
            v = self.vertices[self.v_indices_floor[point_index]]
            glVertex3fv(v)
        glEnd()
        self.drawcalls += 1
        self.reset_transform()
    
    def draw_ceiling(self, element: int, row: int, col: int) -> None:
        
        glBindTexture(GL_TEXTURE_2D, self.floor_textures[element])
        self.apply_transform(row, col)

        glBegin(GL_TRIANGLE_FAN)
        for point_index in range(4):
            t = self.tex_coords[self.t_indices_ceiling[point_index]]
            glTexCoord2fv(t)
            v = self.vertices[self.v_indices_ceiling[point_index]]
            glVertex3fv(v)
        glEnd()
        self.drawcalls += 1
        self.reset_transform()