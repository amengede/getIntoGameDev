import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
import math

def createShader(vertexFilepath, fragmentFilepath):
    """
        Compile and link a shader program from source.

        Parameters:

            vertexFilepath: filepath to the vertex shader source code (relative to this file)

            fragmentFilepath: filepath to the fragment shader source code (relative to this file)
        
        Returns:

            An integer, being a handle to the shader location on the graphics card
    """

    with open(vertexFilepath,'r') as f:
        vertex_src = f.readlines()

    with open(fragmentFilepath,'r') as f:
        fragment_src = f.readlines()
    
    shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                            compileShader(fragment_src, GL_FRAGMENT_SHADER))
    
    return shader

class Entity:
    """ A basic entity in the game, anything with position and rotation """

    def __init__(self, position: list[float], eulers: list[float]):
        """ Initialise an entity at the given position with the given rotation. """

        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)
    
    def make_transform(self, parent_transform: np.ndarray) -> np.ndarray:
        
        model_transform = pyrr.matrix44.create_identity(np.float32)

        model_transform = pyrr.matrix44.multiply(
            m1 = model_transform,
            m2 = pyrr.matrix44.create_from_x_rotation(
                theta = np.radians(self.eulers[0]),
                dtype = np.float32
            )
        )

        model_transform = pyrr.matrix44.multiply(
            m1 = model_transform,
            m2 = pyrr.matrix44.create_from_y_rotation(
                theta = np.radians(self.eulers[1]),
                dtype = np.float32
            )
        )

        model_transform = pyrr.matrix44.multiply(
            m1 = model_transform,
            m2 = pyrr.matrix44.create_from_translation(
                vec = self.position,
                dtype = np.float32
            )
        )

        model_transform = pyrr.matrix44.multiply(
            m1 = model_transform,
            m2 = parent_transform
        )

        return model_transform

class Board(Entity):


    def __init__(self, position: list[float], eulers: list[float]):
        """ Create a board and all its pieces. """

        super().__init__(position, eulers)

        self.layout = [
            [1,1,1,1,1,1,1,1,1,1],
            [1,0,1,0,1,0,1,0,0,1],
            [1,0,1,0,0,0,1,0,1,1],
            [1,0,0,0,1,1,1,2,0,1],
            [1,0,1,0,0,0,0,0,1,1],
            [1,0,1,0,1,1,1,0,1,1],
            [1,0,1,0,1,0,0,0,1,1],
            [1,0,1,0,1,1,1,0,1,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1]
        ]

        self.pieces: list[Entity] = []
        self.ball: Ball = None
        for row, row_contents in enumerate(self.layout):
            for col, flag in enumerate(row_contents):

                if flag == 1:
                    self.pieces.append(
                        Entity(
                            position = [2 * col - 9, 2 * row - 9, 2],
                            eulers   = [0, 0, 0]
                        )
                    )
                
                elif flag == 2:
                    self.ball = Ball(
                        position = [2 * col - 9, 2 * row - 9, 2],
                        color = [1, 1, 1]
                    )
                    self.layout[row][col] = 0

        self.maxTilt = 30
    
    def tilt(self, amount):

        (dx, dy) = amount

        self.eulers[0] = min(self.maxTilt,max(-self.maxTilt, self.eulers[0] + dx))
        self.eulers[1] = min(self.maxTilt,max(-self.maxTilt, self.eulers[1] + dy))

    def update(self) -> None:
        """ Update the state of the board and its pieces """

        self.ball.velocity[0] += -0.01*np.sin(np.radians(self.eulers[1]))
        self.ball.velocity[1] += 0.01*np.sin(np.radians(self.eulers[0]))
        self.ball.update(self.layout)

class Ball(Entity):


    def __init__(self, position: list[float], color: list[float]):
        """ Create a ball at the given position with the given color """

        super().__init__(position = position, eulers = [0,0,0])
        self.velocity = [0,0]
        self.color = np.array(color, dtype=np.float32)
    
    def update(self, environmentLayout: list[list[int]]) -> None:
        """
            Attempt to move around the environment

            Parameters:

                environmentLayout: a 2D array of integers representing the pieces.
                                    0: empty, 1: blocked
        """

        testCol = math.floor((self.position[0] + 1 + 0.75*np.sign(self.velocity[0]) + self.velocity[0] + 9) / 2)
        testRow = math.floor((self.position[1] + 1 + 0.75*np.sign(self.velocity[1]) + self.velocity[1] + 9) / 2)
        currentCol = math.floor((self.position[0] + 1 + 9) / 2)
        currentRow = math.floor((self.position[1] + 1 + 9) / 2)
        #check row
        if testRow > 9 \
            or testRow < 0 \
            or environmentLayout[testRow][currentCol] == 1:
            self.velocity[1] *= -0.25
        #check column
        if testCol > 9 \
            or testCol < 0 \
            or environmentLayout[currentRow][testCol] == 1:
            self.velocity[0] *= -0.25
        self.position[0] = min(9, max(-9, self.position[0] + self.velocity[0]))
        self.position[1] = min(9, max(-9, self.position[1] + self.velocity[1]))

class App:
    """ The game."""


    def __init__(self):
        """ Start the app up """
        
        self.initialise_pygame()
        
        self.make_assets()

        self.set_onetime_shader_data()

        self.get_uniform_locations()

        self.mainLoop()
    
    def initialise_pygame(self) -> None:
        """ Set up pygame environment. """

        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((640,480), pg.OPENGL|pg.DOUBLEBUF)
        self.clock = pg.time.Clock()

    def make_assets(self) -> None:
        """ Create any assets which will be used by the game. """

        self.board_texture = Material("gfx/dark_marble.jpg")
        self.piece_texture = Material("gfx/red.jpg")
        self.board_mesh = Mesh("models/board.obj")
        self.piece_mesh = Mesh("models/piece.obj")
        self.ball_mesh = Mesh("models/ball.obj")

        self.board = Board(
            position = [0,0,0],
            eulers = [0,0,0]
        )

        self.shaders = {}
        self.shaders["textured"] = createShader("shaders/vertex.txt", "shaders/fragment.txt")
        self.shaders["colored"] = createShader("shaders/vertexColored.txt", "shaders/fragmentColored.txt")
        
    def set_onetime_shader_data(self) -> None:
        """ Upload any uniform data which only needs to be set once"""

        viewProjection_transform = pyrr.matrix44.multiply(
            m1 = pyrr.matrix44.create_look_at(
                eye = np.array([0, -10, 30]),
                target = np.array([1, 1, 0]),
                up = pyrr.vector.normalize(np.array([0, 1, 2/3])),
                dtype = np.float32
            ),
            m2 = pyrr.matrix44.create_perspective_projection(
                fovy = 45, aspect = 640/480, 
                near = 0.1, far = 80, dtype=np.float32
            )
        )

        sunColor = np.array([1,1,1], dtype=np.float32)

        sunDirection = pyrr.vector.normalize(np.array([1,0,-1], dtype=np.float32))

        glUseProgram(self.shaders["textured"])
        #declare that "imageTexture" is texture unit 0
        glUniform1i(glGetUniformLocation(self.shaders["textured"], "imageTexture"), 0)
        #upload view & projection transform
        glUniformMatrix4fv(
            glGetUniformLocation(self.shaders["textured"],"viewProjection"),
            1, GL_FALSE, viewProjection_transform
        )
        #upload sun color
        glUniform3fv(
            glGetUniformLocation(self.shaders["textured"],"sunColor"),
            1, sunColor
        )
        #upload sun direction
        glUniform3fv(
            glGetUniformLocation(self.shaders["textured"],"sunDirection"),
            1, sunDirection
        )

        glUseProgram(self.shaders["colored"])
        #upload view & projection transform
        glUniformMatrix4fv(
            glGetUniformLocation(self.shaders["colored"], "viewProjection"),
            1, GL_FALSE, viewProjection_transform
        )
        #upload sun color
        glUniform3fv(
            glGetUniformLocation(self.shaders["colored"], "sunColor"), 
            1, sunColor
        )
        #upload sun direction
        glUniform3fv(
            glGetUniformLocation(self.shaders["colored"],"sunDirection"), 
            1, sunDirection
        )
    
    def get_uniform_locations(self) -> None:
        """ Query and store the locations of uniforms which need to be set every frame. """

        self.modelLocations = {}

        glUseProgram(self.shaders["textured"])
        self.modelLocations["textured"] = glGetUniformLocation(self.shaders["textured"], "model")

        glUseProgram(self.shaders["colored"])
        self.modelLocations["colored"] = glGetUniformLocation(self.shaders["colored"], "model")
        self.colorLocation = glGetUniformLocation(self.shaders["colored"], "objectColor")

    def mainLoop(self) -> None:
        """ Run the app."""

        glClearColor(0, 0, 0, 1)
        glEnable(GL_DEPTH_TEST)
        running = True

        while (running):
            #check events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
            
            self.handle_keys()
            self.board.update()
            
            #refresh screen
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            glUseProgram(self.shaders["textured"])
            board_transform = self.draw_board()
            self.draw_pieces(board_transform)
            
            glUseProgram(self.shaders["colored"])
            self.draw_ball(board_transform)

            pg.display.flip()

            #timing
            self.clock.tick(60)
        self.quit()
    
    def handle_keys(self) -> None:
        """ Tilt the board based on which keys are currently pressed"""

        tiltAmount = [0,0]
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            tiltAmount[1] = 0.4
        if keys[pg.K_RIGHT]:
            tiltAmount[1] = -0.4
        if keys[pg.K_UP]:
            tiltAmount[0] = 0.4
        if keys[pg.K_DOWN]:
            tiltAmount[0] = -0.4
        self.board.tilt(tiltAmount)

    def draw_board(self) -> np.ndarray:
        """ 
            Draw the board and return its transform so that objects further down in the
            hierarchy can use it.
        """

        board_transform = self.board.make_transform(
            parent_transform = pyrr.matrix44.create_identity(dtype = np.float32)
        )
        glUniformMatrix4fv(self.modelLocations["textured"],1,GL_FALSE,board_transform)
        self.board_texture.use()
        glBindVertexArray(self.board_mesh.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.board_mesh.vertex_count)

        return board_transform

    def draw_pieces(self, board_transform: np.ndarray) -> None:
        """
            Draw the pieces on the board
        """

        self.piece_texture.use()
        glBindVertexArray(self.piece_mesh.vao)
        for piece in self.board.pieces:
            glUniformMatrix4fv(
                self.modelLocations["textured"],1,GL_FALSE,
                piece.make_transform(parent_transform = board_transform)
            )
            glDrawArrays(GL_TRIANGLES, 0, self.piece_mesh.vertex_count)

    def draw_ball(self, board_transform: np.ndarray) -> None:
        """
            Draw the ball on the board.
        """

        glBindVertexArray(self.ball_mesh.vao)
        glUniformMatrix4fv(
            self.modelLocations["colored"], 1, GL_FALSE,
            self.board.ball.make_transform(parent_transform = board_transform)
        )
        glUniform3fv(self.colorLocation, 1, self.board.ball.color)
        glDrawArrays(GL_TRIANGLES, 0, self.ball_mesh.vertex_count)

    def quit(self) -> None:
        """ Free any allocated memory. """

        self.board_mesh.destroy()
        self.piece_mesh.destroy()
        self.ball_mesh.destroy()
        self.board_texture.destroy()
        self.piece_texture.destroy()
        glDeleteProgram(self.shaders["textured"])
        glDeleteProgram(self.shaders["colored"])
        pg.quit()

class Mesh:
    """ A mesh which can be loaded from an obj file. """


    def __init__(self, filename):
        """ Load the given file, create a buffer and upload to it. """

        # x, y, z, s, t, nx, ny, nz
        self.v = []
        self.vt = []
        self.vn = []
        self.vertices = []
        self.loadMesh(filename)
        self.vertex_count = len(self.vertices)//8
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        #Free the temporary memory
        self.vertices = []
        #position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        #texture
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        #normal
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))
    
    def loadMesh(self, filename):

        #open the obj file and read the data
        with open(filename,'r') as f:
            line = f.readline()
            while line:
                
                words = line.split(" ")
                if words[0]=="v":
                    self.read_vertex_data(words)
                elif words[0]=="vt":
                    self.read_texture_coordinate_data(words)
                elif words[0]=="vn":
                    self.read_normal_data(words)
                elif words[0]=="f":
                    self.read_face_data(words)
                line = f.readline()
        #Free the temporary memory
        self.v = []
        self.vt = []
        self.vn = []
    
    def read_vertex_data(self, words: list[str]) -> None:
        """ Append the given vertex description to the vertex set."""
        
        new_vertex = [float(words[1]), float(words[2]), float(words[3])]
        self.v.append(new_vertex)
    
    def read_texture_coordinate_data(self, words: list[str]) -> None:
        """ Append the given texture coordinate description to the texcoord set."""
        
        new_tex_coord = [float(words[1]), float(words[2])]
        self.vt.append(new_tex_coord)
    
    def read_normal_data(self, words: list[str]) -> None:
        """ Append the given normal description to the normal set."""
        
        new_normal = [float(words[1]), float(words[2]), float(words[3])]
        self.vn.append(new_normal)
    
    def read_face_data(self, words: list[str]) -> None:
        
        # obj file uses triangle fan format for each face individually.
        triangleCount = len(words) - 3
        for i in range(triangleCount):
            self.read_corner(words[1])
            self.read_corner(words[i+2])
            self.read_corner(words[i+3])
    
    def read_corner(self, description: str) -> None:

        v_vt_vn = description.split("/")
        for element in self.v[int(v_vt_vn[0]) - 1]:
            self.vertices.append(element)
        for element in self.vt[int(v_vt_vn[1]) - 1]:
            self.vertices.append(element)
        for element in self.vn[int(v_vt_vn[2]) - 1]:
            self.vertices.append(element)

    def destroy(self) -> None:
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1,(self.vbo,))

class Material:

    
    def __init__(self, filepath: str):
        """ Make a texture and load it from the given filepath. """

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(filepath).convert()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self) -> None:
        """ Bind the texture for use. """
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.texture)

    def destroy(self):
        """ Free the texture from memory. """
        glDeleteTextures(1, (self.texture,))

myApp = App()