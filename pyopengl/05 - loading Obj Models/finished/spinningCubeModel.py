import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr

def loadMesh(filename: str) -> tuple[list[int], list[float]]:
    """
        Read an obj file.

        Parameters:
            filename: The path to an obj file

        Returns:
            the indices and vertices as lists
    """

    #raw, unassembled data
    v: list[list[float]] = []
    vt: list[list[float]] = []
    vn: list[list[float]] = []

    #for checking unique vertices
    vertexLookup: dict[tuple[int], int] = {}
    
    #final, assembled and packed result
    vertices = []
    indices = []

    #open the obj file and read the data
    with open(filename,'r') as file:

        line = file.readline()
        while line:

            match line[0:line.find(" ")]:
                
                case "v":
                    read_vertex_entry(line, v)
                case "vt":
                    read_vertex_texture_entry(line, vt)
                case "vn":
                    read_vertex_normal_entry(line, vn)
                case "f":
                    read_face_entry(line, 
                        v, vt, vn, 
                        vertexLookup, 
                        indices, vertices
                    )
                case _:
                    pass
            line = file.readline()
        return (indices, vertices)

def read_vertex_entry(line: str, v: list[list[float]]) -> None:
    """
        Read an obj vertex line and append to a list.

        Parameters:
            line: The line to read, should be in the form
            "v x y z"

            v: The list to accumulate vertex data in, should be in the form
            [[x1,y1,z1], [x2,y2,z2], ...]
    """

    #print(v)
    line = line.replace("v ","")
    line = line.split(" ")
    v.append([float(x) for x in line])

def read_vertex_texture_entry(line: str, vt: list[list[float]]) -> None:
    """
        Read an obj tex coordinate line and append to a list.

        Parameters:
            line: The line to read, should be in the form
            "vt u v"

            vt: The list to accumulate texcoord data in, should be in the form
            [[u1,v1], [u2,v2], ...]
    """

    #print(vt)
    line = line.replace("vt ","")
    line = line.split(" ")
    vt.append([float(x) for x in line])

def read_vertex_normal_entry(line: str, vn: list[list[float]]) -> None:
    """
        Read an obj normal line and append to a list.

        Parameters:
            line: The line to read, should be in the form
            "vn x y z"

            vn: The list to accumulate normal data in, should be in the form
            [[x1,y1,z1], [x2,y2,z2], ...]
    """

    #print(vn)
    line = line.replace("vn ","")
    line = line.split(" ")
    vn.append([float(x) for x in line])

def read_face_entry(
    line: str, 
    v: list[list[float]], vt: list[list[float]], vn: list[list[float]], 
    vertexLookup: dict[tuple[int], int], 
    indices: list[int], vertices: list[float]) -> None:
    """
        Read an obj face entry, assemble the described face, and store its data.

        Parameters:
            line: The line, should be of the form
            "f v1/vt1/vn1 v2/vt2/vn2 ..."

            v: The list of vertices stored so far, should be of the form
            [[x1,y1,z1], [x2,y2,z2], ...]

            vt: The list of tex coords stored so far, should be of the form
            [[u1,v1], [u2,v2], ...]

            vn: The list of normals stored to far, should be of the form
            [[x1,y1,z1], [x2,y2,z2], ...]

            vertexLookup: A dictionary storing the index of the given (v,vt,vn)
            tuple in the vertices list, if it's been seen before.

            indices: The final list of indices

            vertices: The final list of vertices
    """

    #print(vertices)
    #print(indices)

    line = line.replace("f ","")
    line = line.replace("\n","")
    line = line.split(" ")
    points = []
    for combo in line:
        components = combo.split("/")
        point = (int(components[0]) - 1, int(components[1]) - 1, int(components[2]) - 1)
        points.append(point)
    
    #assemble face, obj file uses triangle fan format for each face individually.
    triangleCount = len(line) - 2
    unfannedPointIndices = []
    """
        eg. 0,1,2,3 unpacks to vertices: [0,1,2,0,2,3]
    """
    for i in range(triangleCount):
        unfannedPointIndices.append(0)
        unfannedPointIndices.append(i+1)
        unfannedPointIndices.append(i+2)
    
    #check each point
    for pointIndex in unfannedPointIndices:
        point = points[pointIndex]
        if point in vertexLookup:
            indices.append(vertexLookup[point])
        else:
            vertexLookup[point] = int(len(vertices)//8)
            indices.append(vertexLookup[point])
            vertices.extend(v[point[0]])
            vertices.extend(vt[point[1]])
            vertices.extend(vn[point[2]])
    
class Cube:


    def __init__(self, position, eulers):

        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)

class App:
    def __init__(self):
        #initialise pygame
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((640,480), pg.OPENGL|pg.DOUBLEBUF)
        self.clock = pg.time.Clock()
        #initialise opengl
        glClearColor(0.1, 0.2, 0.2, 1)
        self.cube_mesh = Mesh("models/cube.obj")
        self.shader = self.createShader("shaders/vertex.txt", "shaders/fragment.txt")
        glUseProgram(self.shader)
        glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)
        glEnable(GL_DEPTH_TEST)

        self.wood_texture = Material("gfx/wood.jpeg")

        self.cube = Cube(
            position = [0,0,-3],
            eulers = [0,0,0]
        )

        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = 640/480, 
            near = 0.1, far = 10, dtype=np.float32
        )
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader,"projection"),
            1, GL_FALSE, projection_transform
        )
        self.modelMatrixLocation = glGetUniformLocation(self.shader,"model")
        self.mainLoop()

    def createShader(self, vertexFilepath, fragmentFilepath):

        with open(vertexFilepath,'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath,'r') as f:
            fragment_src = f.readlines()
        
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        
        return shader

    def mainLoop(self):
        running = True
        while (running):
            #check events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
            
            #update cube
            self.cube.eulers[2] += 0.25
            if self.cube.eulers[2] > 360:
                self.cube.eulers[2] -= 360
            
            #refresh screen
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glUseProgram(self.shader)

            model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
            """
                pitch: rotation around x axis
                roll:rotation around z axis
                yaw: rotation around y axis
            """
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform, 
                m2=pyrr.matrix44.create_from_eulers(
                    eulers=np.radians(self.cube.eulers), dtype=np.float32
                )
            )
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform, 
                m2=pyrr.matrix44.create_from_translation(
                    vec=np.array(self.cube.position),dtype=np.float32
                )
            )
            glUniformMatrix4fv(self.modelMatrixLocation,1,GL_FALSE,model_transform)
            self.wood_texture.use()
            glBindVertexArray(self.cube_mesh.vao)
            glDrawElements(GL_TRIANGLES, self.cube_mesh.indexCount, GL_UNSIGNED_INT, 0)

            pg.display.flip()

            #timing
            self.clock.tick(60)
        self.quit()

    def quit(self):
        self.cube_mesh.destroy()
        self.wood_texture.destroy()
        glDeleteProgram(self.shader)
        pg.quit()

class Mesh:

    def __init__(self, filename):
        # x, y, z, s, t, nx, ny, nz
        self.indices, self.vertices = loadMesh(filename)
        self.vertex_count = len(self.vertices)//8
        self.indexCount = len(self.indices)
        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.indices = np.array(self.indices, dtype=np.uint32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        #Vertices
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        #position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        #texture
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))

        #Indices
        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)
    
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(2,(self.vbo, self.ebo))

class Material:

    
    def __init__(self, filepath):
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(filepath).convert()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.texture)

    def destroy(self):
        glDeleteTextures(1, (self.texture,))

myApp = App()