from config import *
import megatexture

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
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        
        glUseProgram(self.shader)
        
        self.createQuad()
        self.createNoiseTexture()
        self.createResourceImages()
        self.createLODChain()
        self.createColorBuffers()
        self.createMegaTexture()
    
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
    
    def createNoiseTexture(self):

        self.noiseTextures = []

        for i in range(4):
            noise = []
            for pixel in range(1024):
                vector = randomInUnitSphere()
                noise.append(vector[0])
                noise.append(vector[1])
                noise.append(vector[2])
            noise = np.array(noise, dtype=np.float32)

            noiseTexture = glGenTextures(1)
            glActiveTexture(GL_TEXTURE1 + i)
            glBindTexture(GL_TEXTURE_2D, noiseTexture)

            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

            
            glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA32F,32,32,0,GL_RGB,GL_FLOAT,bytes(noise))

            self.noiseTextures.append(noiseTexture)

    def createResourceImages(self):

        """
            allocate storage for up to 1024 spheres and 1024 planes (why not?)
        """

        sphereData = []

        for i in range(1024):
            for attribute in range(8):
                sphereData.append(0.0)
        self.sphereData = np.array(sphereData, dtype=np.float32)

        self.sphereDataTexture = glGenTextures(1)
        glActiveTexture(GL_TEXTURE5)
        glBindTexture(GL_TEXTURE_2D, self.sphereDataTexture)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA32F,2,1024,0,GL_RGBA,GL_FLOAT,bytes(self.sphereData))

        planeData = []

        for i in range(1024):
            for attribute in range(20):
                planeData.append(0.0)
        self.planeData = np.array(planeData, dtype=np.float32)

        self.planeDataTexture = glGenTextures(1)
        glActiveTexture(GL_TEXTURE6)
        glBindTexture(GL_TEXTURE_2D, self.planeDataTexture)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA32F,5,1024,0,GL_RGBA,GL_FLOAT,bytes(self.planeData))
    
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
    
    def createMegaTexture(self):

        filenames = [
            "AlienArchitecture", "AlternatingColumnsConcreteTile", "BiomechanicalPlumbing", 
            "CarvedStoneFloorCheckered", "ChemicalStrippedConcrete", "ClayBrick",
            "CrumblingBrickWall", "DiamondSquareFlourishTiles", "EgyptianHieroglyphMetal", 
            "FancyHotelWallDirty", "LatheAndPlasterWall"
        ]

        self.megaTexture = megatexture.MegaTexture(filenames)
    
    def adaptResolution(self, frameRate):

        if frameRate > self.targetFrameRate + self.frameRateMargin and self.resolutionLevel > 0:
            #increase resolution
            self.resolutionLevel -= 1
        elif frameRate < self.targetFrameRate - self.frameRateMargin and self.resolutionLevel < len(self.resolutions) - 1:
            #reduce resolution
            self.resolutionLevel += 1
        
        self.screenWidth,self.screenHeight = self.resolutions[self.resolutionLevel]
        self.colorBuffer = self.colorBuffers[self.resolutionLevel]

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

    def fetchDeviceLimits(self):

        self.workGroupCountX = glGetIntegeri_v(GL_MAX_COMPUTE_WORK_GROUP_COUNT, 0)[0]
        self.workGroupCountY = glGetIntegeri_v(GL_MAX_COMPUTE_WORK_GROUP_COUNT, 1)[0]
        self.workGroupCountZ = glGetIntegeri_v(GL_MAX_COMPUTE_WORK_GROUP_COUNT, 2)[0]
        
        self.workGroupSizeX = glGetIntegeri_v(GL_MAX_COMPUTE_WORK_GROUP_SIZE, 0)[0]
        self.workGroupSizeY = glGetIntegeri_v(GL_MAX_COMPUTE_WORK_GROUP_SIZE, 1)[0]
        self.workGroupSizeZ = glGetIntegeri_v(GL_MAX_COMPUTE_WORK_GROUP_SIZE, 2)[0]

        self.workGroupInvocations = glGetIntegerv(GL_MAX_COMPUTE_WORK_GROUP_INVOCATIONS)

        print(f"max global (total) work group counts x:{self.workGroupCountX} y:{self.workGroupCountY} z:{self.workGroupCountZ}")
        print(f"max global (total) work group sizes x:{self.workGroupSizeX} y:{self.workGroupSizeY} z:{self.workGroupSizeZ}")
        print(f"max local work group invocations: {self.workGroupInvocations}")
    
    def recordSphereData(self, i, sphereCount, sphere):

        self.sphereData[8*(i + sphereCount)    ] = sphere.center[0]
        self.sphereData[8*(i + sphereCount) + 1] = sphere.center[1]
        self.sphereData[8*(i + sphereCount) + 2] = sphere.center[2]

        self.sphereData[8*(i + sphereCount) + 3] = sphere.radius

        self.sphereData[8*(i + sphereCount) + 4] = sphere.material
    
    def recordPlaneData(self, i, planeCount, plane):

        self.planeData[20*(i + planeCount)     ] = plane.normal[0]
        self.planeData[20*(i + planeCount) +  1] = plane.normal[1]
        self.planeData[20*(i + planeCount) +  2] = plane.normal[2]

        self.planeData[20*(i + planeCount) +  3] = plane.center[0]
        self.planeData[20*(i + planeCount) +  4] = plane.center[1]
        self.planeData[20*(i + planeCount) +  5] = plane.center[2]

        self.planeData[20*(i + planeCount) +  6] = plane.tangent[0]
        self.planeData[20*(i + planeCount) +  7] = plane.tangent[1]
        self.planeData[20*(i + planeCount) +  8] = plane.tangent[2]

        self.planeData[20*(i + planeCount) +  9] = plane.bitangent[0]
        self.planeData[20*(i + planeCount) + 10] = plane.bitangent[1]
        self.planeData[20*(i + planeCount) + 11] = plane.bitangent[2]
        
        self.planeData[20*(i + planeCount) + 12] = plane.uMin
        self.planeData[20*(i + planeCount) + 13] = plane.uMax
        self.planeData[20*(i + planeCount) + 14] = plane.vMin
        self.planeData[20*(i + planeCount) + 15] = plane.vMax

        self.planeData[20*(i + planeCount) + 16] = plane.material
    
    def updateDataResources(self, scene):

        glUseProgram(self.rayTracerShader)

        scene.outdated = False

        sphereCount = 0

        for i,sphere in enumerate(scene.spheres):

            self.recordSphereData(i, sphereCount, sphere)
            
        sphereCount += len(scene.spheres)

        for room in scene.active_rooms:

            for i,sphere in enumerate(room.spheres):

                self.recordSphereData(i, sphereCount, sphere)

            sphereCount += len(room.spheres)
            

        glUniform1f(glGetUniformLocation(self.rayTracerShader, "sphereCount"), sphereCount)

        glActiveTexture(GL_TEXTURE5)
        glBindTexture(GL_TEXTURE_2D, self.sphereDataTexture)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA32F,2,1024,0,GL_RGBA,GL_FLOAT,bytes(self.sphereData))

        planeCount = 0

        for i,plane in enumerate(scene.planes):

            self.recordPlaneData(i, planeCount, plane)
            
        planeCount += len(scene.planes)
        
        for room in scene.active_rooms:

            for i,plane in enumerate(room.planes):

                self.recordPlaneData(i, planeCount, plane)
            
            planeCount += len(room.planes)
        
        for door in scene.active_rooms[0].doors:

            for i,plane in enumerate(door.planes):

                self.recordPlaneData(i, planeCount, plane)
            
            planeCount += len(door.planes)
        
        glUniform1f(glGetUniformLocation(self.rayTracerShader, "planeCount"), planeCount)

        glActiveTexture(GL_TEXTURE6)
        glBindTexture(GL_TEXTURE_2D, self.planeDataTexture)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA32F,5,1024,0,GL_RGBA,GL_FLOAT,bytes(self.planeData))
    
    def prepareComputeShader(self, scene):

        glUseProgram(self.rayTracerShader)

        glActiveTexture(GL_TEXTURE0)
        glBindImageTexture(0, self.colorBuffer, 0, GL_FALSE, 0, GL_WRITE_ONLY, GL_RGBA32F)

        #noise textures
        for i in range(4):
            glActiveTexture(GL_TEXTURE1 + i)
            glBindImageTexture(1 + i, self.noiseTextures[i], 0, GL_FALSE, 0, GL_READ_ONLY, GL_RGBA32F)

        glActiveTexture(GL_TEXTURE5)
        glBindImageTexture(5, self.sphereDataTexture, 0, GL_FALSE, 0, GL_READ_ONLY, GL_RGBA32F)

        glActiveTexture(GL_TEXTURE6)
        glBindImageTexture(6, self.planeDataTexture, 0, GL_FALSE, 0, GL_READ_ONLY, GL_RGBA32F)

        glActiveTexture(GL_TEXTURE7)
        glBindImageTexture(7, self.megaTexture.texture, 0, GL_FALSE, 0, GL_READ_ONLY, GL_RGBA32F)

        #write material data

        for i,material in enumerate(scene.materials):
            glUniform3fv(glGetUniformLocation(self.rayTracerShader, f"materials[{i}].color"), 1, material.color)
            glUniform1f(glGetUniformLocation(self.rayTracerShader, f"materials[{i}].gloss"), material.reflectance)
        
        #write camera data
        glUniform3fv(glGetUniformLocation(self.rayTracerShader, "viewer.forwards"), 1, scene.camera.forwards)
        glUniform3fv(glGetUniformLocation(self.rayTracerShader, "viewer.up"), 1, scene.camera.up)
        glUniform3fv(glGetUniformLocation(self.rayTracerShader, "viewer.right"), 1, scene.camera.right)
        glUniform3fv(glGetUniformLocation(self.rayTracerShader, "viewer.position"), 1, scene.camera.position)
        glUniformMatrix4fv(glGetUniformLocation(self.rayTracerShader, "view"), 
            1, False, pyrr.matrix44.create_look_at(
                eye = scene.camera.position,
                target = scene.camera.position + scene.camera.forwards,
                up = scene.camera.up,
                dtype = np.float32
            )
        )

    def renderScene(self, scene):
        """
            Draw all objects in the scene
        """
        
        if scene.outdated:
            self.updateDataResources(scene)

        self.prepareComputeShader(scene)
        
        glDispatchCompute(self.screenWidth, self.screenHeight, 1)
  
        # make sure writing to image has finished before read
        glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)
        glBindImageTexture(0, 0, 0, GL_FALSE, 0, GL_WRITE_ONLY, GL_RGBA32F)
        self.drawScreen()

    def drawScreen(self):
        glUseProgram(self.shader)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.colorBuffer)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        pg.display.flip()
    
    def destroy(self):
        """
            Free any allocated memory
        """
        glUseProgram(self.rayTracerShader)
        glMemoryBarrier(GL_ALL_BARRIER_BITS)
        glDeleteProgram(self.rayTracerShader)
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))
        glDeleteTextures(len(self.colorBuffers), self.colorBuffers)
        glDeleteProgram(self.shader)