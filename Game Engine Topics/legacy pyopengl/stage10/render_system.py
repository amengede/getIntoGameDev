from config import *
import component_registry

class RenderSystem:

    def __init__(self, registry: component_registry.ComponentRegistry):

        self.set_up_opengl()

        self.texture = self.load_texture("img/stella.png")
        self.set_up_plane_model()

        self.plane_positions = registry.plane_center
        self.plane_thetas = registry.plane_theta
        self.light_position = registry.light_position
        self.ambient_color = registry.ambient_color
        self.diffuse_color = registry.diffuse_color
    
    def set_up_opengl(self) -> None:

        gluPerspective(45, 640 / 480, 0.1, 50.0)

        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)

    def set_up_plane_model(self) -> None:
        self.vertices = np.array((
            ( 1, -1, 0), ( 1,  1, 0), 
            (-1,  1, 0), (-1, -1, 0)), dtype=np.float32)

        self.colors = np.array((
            (0,0,1), (0,1,0), 
            (0,1,1), (1,0,0)), dtype=np.float32)

        self.tex_coords = np.array(((1,1), (1,0), (0,0), (0,1)), dtype=np.float32)

        self.normal = np.array((0, 0, 1), dtype=np.float32)

        self.indices = np.array(((0, 1, 2, 3),), dtype = np.uint8)

    def reset_transform(self) -> None:

        glPopMatrix()

    def apply_rotation(self, theta: float) -> np.ndarray:

        glPushMatrix()
        glRotatef(theta, 0, 1, 0)

        #construct rotation matrix
        c = np.cos(np.radians(theta))
        s = np.sin(np.radians(theta))

        m = np.array(
            ((c, 0, -s),
            (0, 1, 0),
            (s, 0, c)),
            dtype = np.float32)

        return m.dot(self.normal)

    def load_texture(self, filename: str) -> int:

        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        
        image = pg.image.load(filename).convert_alpha()
        width, height = image.get_rect().size
        data = pg.image.tobytes(image, "RGBA")
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        return texture

    def update(self) -> None:
        
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        
        for i in range(len(self.plane_thetas)):
            
            theta = self.plane_thetas[i]
            pos = self.plane_positions[i]
            normal = self.apply_rotation(theta)
            self.draw_filled(pos, normal)
            self.reset_transform()
        self.reset_transform()
        pg.display.flip()

    def draw_filled(self, position: np.ndarray, normal: np.ndarray) -> None:
        
        glBindTexture(GL_TEXTURE_2D, self.texture)

        light = self.ambient_color.copy()
        light_to_plane = self.light_position - position

        for face_index, edge_table in enumerate(self.indices):

            light += self.diffuse_color * max(0.0, np.dot(light_to_plane, normal))

            glBegin(GL_TRIANGLE_FAN)
            
            for index in edge_table:
                color = np.multiply(light, self.colors[index])
                glColor3fv(color)
                glTexCoord2fv(self.tex_coords[index])
                glVertex3fv(self.vertices[index])
            glEnd()