from config import *

class Material:
    def __init__(self, filepath):
        self.diffuseTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.diffuseTexture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(f"{filepath}_diffuse.jpg").convert()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)
        
        self.specularTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.specularTexture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(f"{filepath}_specular.jpg").convert()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.diffuseTexture)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D,self.specularTexture)

    def destroy(self):
        glDeleteTextures(2, (self.diffuseTexture, self.specularTexture))

class SimpleMaterial:
    def __init__(self, filepath):
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(f"{filepath}.png").convert_alpha()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA8,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.texture)

    def destroy(self):
        glDeleteTextures(1, (self.texture,))

class CubeMapMaterial:
    def __init__(self, filepath):
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture)

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        #load textures
        image = pg.image.load(f"{filepath}_left.png").convert_alpha()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,0,GL_RGBA8,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)

        image = pg.image.load(f"{filepath}_right.png").convert_alpha()
        image = pg.transform.flip(image,True,True)
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_Y,0,GL_RGBA8,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)

        image = pg.image.load(f"{filepath}_top.png").convert_alpha()
        image = pg.transform.rotate(image, 90)
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_Z,0,GL_RGBA8,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)

        image = pg.image.load(f"{filepath}_bottom.png").convert_alpha()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_CUBE_MAP_NEGATIVE_Z,0,GL_RGBA8,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)

        image = pg.image.load(f"{filepath}_back.png").convert_alpha()
        image = pg.transform.rotate(image, -90)
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_CUBE_MAP_NEGATIVE_X,0,GL_RGBA8,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)

        image = pg.image.load(f"{filepath}_front.png").convert_alpha()
        image = pg.transform.rotate(image, 90)
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X,0,GL_RGBA8,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)

    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP,self.texture)

    def destroy(self):
        glDeleteTextures(1, (self.texture,))

class CubeBasic:
    def __init__(self, shader, l, w, h, r, g, b):
        self.shader = shader
        glUseProgram(shader)
        # x, y, z, r, g, b
        self.vertices = (
                -l/2, -w/2, -h/2, r, g, b,
                -l/2,  w/2, -h/2, r, g, b,
                 l/2,  w/2, -h/2, r, g, b,

                 l/2,  w/2, -h/2, r, g, b,
                 l/2, -w/2, -h/2, r, g, b,
                -l/2, -w/2, -h/2, r, g, b,

                 l/2,  w/2,  h/2, r, g, b,
                -l/2,  w/2,  h/2, r, g, b,
                -l/2, -w/2,  h/2, r, g, b,

                -l/2, -w/2,  h/2, r, g, b,
                 l/2, -w/2,  h/2, r, g, b,
                 l/2,  w/2,  h/2, r, g, b,

                -l/2, -w/2,  h/2, r, g, b,
                -l/2,  w/2,  h/2, r, g, b,
                -l/2,  w/2, -h/2, r, g, b,

                -l/2,  w/2, -h/2, r, g, b,
                -l/2, -w/2, -h/2, r, g, b,
                -l/2, -w/2,  h/2, r, g, b,

                 l/2, -w/2, -h/2, r, g, b,
                 l/2,  w/2, -h/2, r, g, b,
                 l/2,  w/2,  h/2, r, g, b,

                 l/2,  w/2,  h/2, r, g, b,
                 l/2, -w/2,  h/2, r, g, b,
                 l/2, -w/2, -h/2, r, g, b,

                 l/2, -w/2,  h/2, r, g, b,
                -l/2, -w/2,  h/2, r, g, b,
                -l/2, -w/2, -h/2, r, g, b,

                -l/2, -w/2, -h/2, r, g, b,
                 l/2, -w/2, -h/2, r, g, b,
                 l/2, -w/2,  h/2, r, g, b,

                 l/2,  w/2, -h/2, r, g, b,
                -l/2,  w/2, -h/2, r, g, b,
                -l/2,  w/2,  h/2, r, g, b,

                -l/2,  w/2,  h/2, r, g, b,
                 l/2,  w/2,  h/2, r, g, b,
                 l/2,  w/2, -h/2, r, g, b
            )
        self.vertex_count = len(self.vertices)//6
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

    def draw(self, position, shader=None):
        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        model_transform = pyrr.matrix44.multiply(model_transform, pyrr.matrix44.create_from_translation(vec=position,dtype=np.float32))
        if shader is None:
            glUseProgram(self.shader)
            glUniformMatrix4fv(glGetUniformLocation(self.shader,"model"),1,GL_FALSE,model_transform)
        else:
            glUseProgram(shader)
            glUniformMatrix4fv(glGetUniformLocation(shader,"model"),1,GL_FALSE,model_transform)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class ObjModel:
    def __init__(self, folderpath, filename, shader, material):
        self.shader = shader
        self.material = material
        glUseProgram(shader)
        v = []
        vt = []
        vn = []
        self.vertices = []

        #open the obj file and read the data
        with open(f"{folderpath}/{filename}",'r') as f:
            line = f.readline()
            while line:
                firstSpace = line.find(" ")
                flag = line[0:firstSpace]
                if flag=="mtllib":
                    #declaration of material file
                    pass
                elif flag=="v":
                    #vertex
                    line = line.replace("v ","")
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    v.append(l)
                    #print(v)
                elif flag=="vt":
                    #texture coordinate
                    line = line.replace("vt ","")
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    vt.append(l)
                elif flag=="vn":
                    #normal
                    line = line.replace("vn ","")
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    vn.append(l)
                elif flag=="f":
                    #face, four vertices in v/vt/vn form
                    line = line.replace("f ","")
                    line = line.replace("\n","")
                    line = line.split(" ")
                    theseVertices = []
                    theseTextures = []
                    theseNormals = []
                    for vertex in line:
                        l = vertex.split("/")
                        position = int(l[0]) - 1
                        theseVertices.append(v[position])
                        texture = int(l[1]) - 1
                        theseTextures.append(vt[texture])
                        normal = int(l[2]) - 1
                        theseNormals.append(vn[normal])
                    # obj file uses triangle fan format for each face individually.
                    # unpack each face
                    triangles_in_face = len(line) - 2

                    vertex_order = []
                    for i in range(triangles_in_face):
                        vertex_order.append(0)
                        vertex_order.append(i+1)
                        vertex_order.append(i+2)
                    for i in vertex_order:
                        for x in theseVertices[i]:
                            self.vertices.append(x)
                        for x in theseTextures[i]:
                            self.vertices.append(x)
                        for x in theseNormals[i]:
                            self.vertices.append(x)
                    
                line = f.readline()
        self.vertices = np.array(self.vertices,dtype=np.float32)

        #vertex array object, all that stuff
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,self.vbo)
        glBufferData(GL_ARRAY_BUFFER,self.vertices.nbytes,self.vertices,GL_STATIC_DRAW)
        self.vertexCount = int(len(self.vertices)/8)

        #position attribute
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,self.vertices.itemsize*8,ctypes.c_void_p(0))
        #normal attribute
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1,2,GL_FLOAT,GL_FALSE,self.vertices.itemsize*8,ctypes.c_void_p(12))
        #texture attribute
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2,3,GL_FLOAT,GL_FALSE,self.vertices.itemsize*8,ctypes.c_void_p(20))

    def getVertices(self):
        return self.vertices

    def draw(self, position,shader = None):
        self.material.use()
        model_transform = pyrr.matrix44.create_from_translation(position, dtype=np.float32)
        if shader is None:
            glUseProgram(self.shader)
            glUniformMatrix4fv(glGetUniformLocation(self.shader,"model"),1,GL_FALSE,model_transform)
        else:
            glUseProgram(shader)
            glUniformMatrix4fv(glGetUniformLocation(shader,"model"),1,GL_FALSE,model_transform)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES,0,self.vertexCount)
    
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class TexturedQuad:
    def __init__(self, x, y, w, h, textures, shader):
        self.shader = shader
        self.textures = textures
        self.vertices = (
            x - w/2, y + h/2, 0, 1,
            x - w/2, y - h/2, 0, 0,
            x + w/2, y - h/2, 1, 0,

            x - w/2, y + h/2, 0, 1,
            x + w/2, y - h/2, 1, 0,
            x + w/2, y + h/2, 1, 1
        )
        self.vertices = np.array(self.vertices, dtype=np.float32)
        
        glUseProgram(self.shader)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(8))
    
    def draw(self):
        glUseProgram(self.shader)
        for i in range(len(self.textures)):
            glActiveTexture(GL_TEXTURE0 + i)
            glBindTexture(GL_TEXTURE_2D, self.textures[i])
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES,0,6)
    
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class Particle2DCreateInfo:
    def __init__(self):
        self.pos = None
        self.color = None
        self.lifetime = None
        self.velocity_field = None
        self.size = None
        self.layer = None
        self.shader = None

class Particle2D:
    def __init__(self, createInfo):
        self.pos = createInfo.pos
        self.color = createInfo.color
        self.lifetime = createInfo.lifetime
        self.velocity_field = createInfo.velocity_field
        self.size = createInfo.size
        self.layer = createInfo.layer
        self.shader = createInfo.shader
        self.t = 0

        self.vertex = [self.pos[0], self.pos[1], 0, 1]
        self.vertex = np.array(self.vertex, dtype=np.float32)
        glUseProgram(self.shader)
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, self.vertex.nbytes, self.vertex, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
    
    def update(self):
        glUseProgram(self.shader)
        self.t += 1
        velocity = self.velocity_field(self.pos)
        self.pos[0] += velocity[0] / (100 * self.layer)
        self.pos[1] += velocity[1] / (100 * self.layer)
        self.vertex[0] = self.pos[0]
        self.vertex[1] = self.pos[1]
        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, self.vertex.nbytes, self.vertex, GL_STATIC_DRAW)
    
    def draw(self):
        glUseProgram(self.shader)
        color = np.array([self.color[0], self.color[1], self.color[2], max(1 - self.t/self.lifetime, 0)], dtype=np.float32)
        glUniform4fv(glGetUniformLocation(self.shader, "object_color"), 1, color)
        glUniform1f(glGetUniformLocation(self.shader, "size"), self.size)
        glUniform1f(glGetUniformLocation(self.shader, "layer"), self.layer)
        glBindVertexArray(self.VAO)
        glDrawArrays(GL_POINTS, 0, 1)

    def should_destroy(self):
        return self.t >= self.lifetime
    
    def destroy(self):
        glDeleteVertexArrays(1, (self.VAO,))
        glDeleteBuffers(1, (self.VBO,))

class BillBoard:
    def __init__(self, w, h, texture, shader):
        self.texture = texture
        self.shader = shader
        self.vertices = (
            0, -w/2,  h/2, 0, 1, -1, 0, 0,
            0, -w/2, -h/2, 0, 0, -1, 0, 0,
            0,  w/2, -h/2, 1, 0, -1, 0, 0,

            0, -w/2,  h/2, 0, 1, -1, 0, 0,
            0,  w/2, -h/2, 1, 0, -1, 0, 0,
            0,  w/2,  h/2, 1, 1, -1, 0, 0
        )
        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.vertexCount = 6
        
        glUseProgram(self.shader)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))

        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))
    
    def draw(self, position, playerPosition):
        glUseProgram(self.shader)
        self.texture.use()
        directionFromPlayer = position - playerPosition
        angle1 = np.arctan2(-directionFromPlayer[1],directionFromPlayer[0])
        dist2d = math.sqrt(directionFromPlayer[0] ** 2 + directionFromPlayer[1] ** 2)
        angle2 = np.arctan2(directionFromPlayer[2],dist2d)

        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        model_transform = pyrr.matrix44.multiply(model_transform,
            pyrr.matrix44.create_from_y_rotation(theta=angle2, dtype=np.float32))
        model_transform = pyrr.matrix44.multiply(model_transform,
            pyrr.matrix44.create_from_z_rotation(theta=angle1, dtype=np.float32))
        model_transform = pyrr.matrix44.multiply(model_transform,
                            pyrr.matrix44.create_from_translation(position,dtype=np.float32))
        glUniformMatrix4fv(glGetUniformLocation(self.shader,"model"),1,GL_FALSE,model_transform)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertexCount)

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class CubeMapModel:
    def __init__(self, shader, l, w, h, r, g, b, material):
        self.material = material
        self.shader = shader
        glUseProgram(shader)
        # x, y, z, r, g, b
        self.vertices = (
                -l/2, -w/2, -h/2, r, g, b,
                -l/2,  w/2, -h/2, r, g, b,
                 l/2,  w/2, -h/2, r, g, b,

                 l/2,  w/2, -h/2, r, g, b,
                 l/2, -w/2, -h/2, r, g, b,
                -l/2, -w/2, -h/2, r, g, b,

                 l/2,  w/2,  h/2, r, g, b,
                -l/2,  w/2,  h/2, r, g, b,
                -l/2, -w/2,  h/2, r, g, b,

                -l/2, -w/2,  h/2, r, g, b,
                 l/2, -w/2,  h/2, r, g, b,
                 l/2,  w/2,  h/2, r, g, b,

                -l/2, -w/2,  h/2, r, g, b,
                -l/2,  w/2,  h/2, r, g, b,
                -l/2,  w/2, -h/2, r, g, b,

                -l/2,  w/2, -h/2, r, g, b,
                -l/2, -w/2, -h/2, r, g, b,
                -l/2, -w/2,  h/2, r, g, b,

                 l/2, -w/2, -h/2, r, g, b,
                 l/2,  w/2, -h/2, r, g, b,
                 l/2,  w/2,  h/2, r, g, b,

                 l/2,  w/2,  h/2, r, g, b,
                 l/2, -w/2,  h/2, r, g, b,
                 l/2, -w/2, -h/2, r, g, b,

                 l/2, -w/2,  h/2, r, g, b,
                -l/2, -w/2,  h/2, r, g, b,
                -l/2, -w/2, -h/2, r, g, b,

                -l/2, -w/2, -h/2, r, g, b,
                 l/2, -w/2, -h/2, r, g, b,
                 l/2, -w/2,  h/2, r, g, b,

                 l/2,  w/2, -h/2, r, g, b,
                -l/2,  w/2, -h/2, r, g, b,
                -l/2,  w/2,  h/2, r, g, b,

                -l/2,  w/2,  h/2, r, g, b,
                 l/2,  w/2,  h/2, r, g, b,
                 l/2,  w/2, -h/2, r, g, b
            )
        self.vertex_count = len(self.vertices)//6
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

    def draw(self, position, shader = None):
        self.material.use()
        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        model_transform = pyrr.matrix44.multiply(model_transform, pyrr.matrix44.create_from_translation(vec=position,dtype=np.float32))
        if shader is None:
            glUseProgram(self.shader)
            glUniformMatrix4fv(glGetUniformLocation(self.shader,"model"),1,GL_FALSE,model_transform)
        else:
            glUseProgram(shader)
            glUniformMatrix4fv(glGetUniformLocation(shader,"model"),1,GL_FALSE,model_transform)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))