from config import *

class Texture:
    def __init__(self,filepath):
        self._tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,self._tex)
        #texture wrapping
        #s and t: u and v coordinates
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        #texture filtering
        #minifying or magnifying filter
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        #load image
        image = pg.image.load(filepath).convert()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,\
                        0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)
    
    def getTexture(self):
        return self._tex

class ObjModel:
    def __init__(self,filepath):

        attributeMap = {'V':0,'T':1,'N':2}
        datatypeMap = {'F':GL_FLOAT}

        attributes = []

        scene = pwf.Wavefront(filepath)
        for name, material in scene.materials.items():
            vertex_format = material.vertex_format.split("_")
            vertices = material.vertices

        stride = 0
        for item in vertex_format:
            attributeLocation = attributeMap[item[0]]
            attributeStart = stride
            attributeLength = int(item[1])
            attributeDataType = datatypeMap[item[2]]
            stride += attributeLength
            attributes.append((attributeLocation,attributeLength,attributeDataType,attributeStart*4))
        
        self._VAO = glGenVertexArrays(1)
        glBindVertexArray(self._VAO)

        vertices = np.array(vertices,dtype=np.float32)

        self._VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,self._VBO)
        glBufferData(GL_ARRAY_BUFFER,vertices.nbytes,vertices,GL_STATIC_DRAW)
        self._vertexCount = int(len(vertices)/stride)

        for a in attributes:
            glEnableVertexAttribArray(a[0])
            glVertexAttribPointer(a[0],a[1],a[2],GL_FALSE,vertices.itemsize*stride,ctypes.c_void_p(a[3]))

    def getVAO(self):
        return self._VAO

    def getVertexCount(self):
        return self._vertexCount