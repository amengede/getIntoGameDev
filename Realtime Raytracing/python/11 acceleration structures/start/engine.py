from config import *

class Engine:
    """
        Responsible for drawing scenes
    """

    def __init__(self, width, height):
        """
            Initialize a flat raytracing context
            
                Parameters:
                    width (int): width of screen
                    height (int): height of screen
        """
        self.screenWidth = width
        self.screenHeight = height

        self.targetFrameRate = 60
        self.frameRateMargin = 10

        #general OpenGL configuration
        self.shader = self.createShader("shaders/frameBufferVertex.txt",
                                        "shaders/frameBufferFragment.txt")
        
        self.rayTracerShader = self.createComputeShader("shaders/rayTracer.txt")
        
        glUseProgram(self.shader)
        
        self.createQuad()
        self.createLODChain()
        self.createColorBuffers()
        self.createResourceMemory()
    
    def createQuad(self):
        # x, y, z, s, t
        self.vertices = np.array(
            ( 1.0,  1.0, 0.0, 1.0, 1.0, #top-right
             -1.0,  1.0, 0.0, 0.0, 1.0, #top-left
             -1.0, -1.0, 0.0, 0.0, 0.0, #bottom-left
             -1.0, -1.0, 0.0, 0.0, 0.0, #bottom-left
              1.0, -1.0, 0.0, 1.0, 0.0, #bottom-right
              1.0,  1.0, 0.0, 1.0, 1.0), #top-right
             dtype=np.float32
        )

        self.vertex_count = 6

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))
    
    def createLODChain(self):

        self.resolutions = [(self.screenWidth, self.screenHeight)]

        width,height = (self.screenWidth,self.screenHeight)
        while width > 2 and height > 2:
            width = int(width / 1.25)
            height = int(height / 1.25)
            self.resolutions.append((width, height))
        
        self.resolutionLevel = len(self.resolutions) - 1
        
        self.screenWidth,self.screenHeight = self.resolutions[self.resolutionLevel]

    def createColorBuffers(self):

        self.colorBuffers = []

        for resolution in self.resolutions:

            width,height = resolution

            newColorBuffer = glGenTextures(1)
            self.colorBuffers.append(newColorBuffer)
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, newColorBuffer)

            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, width, height, 0, GL_RGBA, GL_FLOAT, None)
        
        self.colorBuffer = self.colorBuffers[self.resolutionLevel]
    
    def createResourceMemory(self):

        """
            allocate storage for up to 1024 objects (why not?)
        """

        # sphere: (cx cy cz r) (r g b roughness)
        self.objectData = np.zeros(8 * 1024, dtype = np.float32)

        self.objectDataTexture = glGenTextures(1)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.objectDataTexture)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA32F, 2, 1024,0,GL_RGBA,GL_FLOAT,bytes(self.objectData))

    def createShader(self, vertexFilepath, fragmentFilepath):
        """
            Read source code, compile and link shaders.
            Returns the compiled and linked program.
        """

        with open(vertexFilepath,'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath,'r') as f:
            fragment_src = f.readlines()
        
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        
        return shader
    
    def createComputeShader(self, filepath):
        """
            Read source code, compile and link shaders.
            Returns the compiled and linked program.
        """

        with open(filepath,'r') as f:
            compute_src = f.readlines()
        
        shader = compileProgram(compileShader(compute_src, GL_COMPUTE_SHADER))
        
        return shader

    def recordSphere(self, i, _sphere):

        # sphere: (cx cy cz r) (r g b roughness)

        self.objectData[8*i]     = _sphere.center[0]
        self.objectData[8*i + 1] = _sphere.center[1]
        self.objectData[8*i + 2] = _sphere.center[2]

        self.objectData[8*i + 3] = _sphere.radius

        self.objectData[8*i + 4] = _sphere.color[0]
        self.objectData[8*i + 5] = _sphere.color[1]
        self.objectData[8*i + 6] = _sphere.color[2]

        self.objectData[8*i + 7] = _sphere.roughness
     
    def updateScene(self, scene):

        scene.outDated = False

        glUseProgram(self.rayTracerShader)

        glUniform1f(glGetUniformLocation(self.rayTracerShader, "sphereCount"), len(scene.spheres))

        for i,_sphere in enumerate(scene.spheres):
            self.recordSphere(i, _sphere)
        
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.objectDataTexture)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA32F,2,1024,0,GL_RGBA,GL_FLOAT,bytes(self.objectData))

    def prepareScene(self, scene):
        """
            Send scene data to the shader.
        """

        glUseProgram(self.rayTracerShader)

        glUniform3fv(glGetUniformLocation(self.rayTracerShader, "viewer.position"), 1, scene.camera.position)
        glUniform3fv(glGetUniformLocation(self.rayTracerShader, "viewer.forwards"), 1, scene.camera.forwards)
        glUniform3fv(glGetUniformLocation(self.rayTracerShader, "viewer.right"), 1, scene.camera.right)
        glUniform3fv(glGetUniformLocation(self.rayTracerShader, "viewer.up"), 1, scene.camera.up)

        if scene.outDated:
            self.updateScene(scene)
        
        glActiveTexture(GL_TEXTURE1)
        glBindImageTexture(1, self.objectDataTexture, 0, GL_FALSE, 0, GL_READ_ONLY, GL_RGBA32F)
  
    def renderScene(self, scene):
        """
            Draw all objects in the scene
        """
        #start = time.time()
        glUseProgram(self.rayTracerShader)

        self.prepareScene(scene)

        glActiveTexture(GL_TEXTURE0)
        glBindImageTexture(0, self.colorBuffer, 0, GL_FALSE, 0, GL_WRITE_ONLY, GL_RGBA32F)
        
        glDispatchCompute(self.screenWidth, self.screenHeight, 1)
  
        # make sure writing to image has finished before read
        glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)
        glBindImageTexture(0, 0, 0, GL_FALSE, 0, GL_WRITE_ONLY, GL_RGBA32F)
        self.drawScreen()
        #finish = time.time()
        #print(f"render took {(finish - start) * 1000} milliseconds.")

    def drawScreen(self):
        glUseProgram(self.shader)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.colorBuffer)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        pg.display.flip()
    
    def adaptResolution(self, frameRate):

        if frameRate > self.targetFrameRate + self.frameRateMargin and self.resolutionLevel > 0:
            #increase resolution
            self.resolutionLevel -= 1
        elif frameRate < self.targetFrameRate - self.frameRateMargin and self.resolutionLevel < len(self.resolutions) - 1:
            #reduce resolution
            self.resolutionLevel += 1
        
        self.screenWidth,self.screenHeight = self.resolutions[self.resolutionLevel]
        self.colorBuffer = self.colorBuffers[self.resolutionLevel]
    
    def destroy(self):
        """
            Free any allocated memory
        """
        glUseProgram(self.rayTracerShader)
        glMemoryBarrier(GL_ALL_BARRIER_BITS)
        glDeleteProgram(self.rayTracerShader)
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))
        glDeleteTextures(1, (self.colorBuffer,))
        glDeleteProgram(self.shader)