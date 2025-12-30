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

        self.shaderGPass = self.createShader(
            "shaders/g_vertex.txt",
            "shaders/g_fragment.txt"
        )

        self.set_onetime_shader_data()

        self.get_shader_locations()
        
        glUseProgram(self.shader)
        
        self.createQuad()
        self.createColorBuffers()
        self.createResourceMemory()
        self.createMegaTexture()
    
    def set_onetime_shader_data(self):

        glUseProgram(self.shaderGPass)

        glUniform1i(
            glGetUniformLocation(
                self.shaderGPass, "megaTexture"
            ), 0
        )
    
    def get_shader_locations(self):

        glUseProgram(self.shaderGPass)

        self.viewMatrixLocation = glGetUniformLocation(
            self.shaderGPass, "view"
        )
        self.projectionMatrixLocation = glGetUniformLocation(
            self.shaderGPass, "projection"
        )

        glUseProgram(self.rayTracerShader)

        self.viewerPositionLocation = glGetUniformLocation(
            self.rayTracerShader, "viewer.position"
        )
        self.viewerForwardsLocation = glGetUniformLocation(
            self.rayTracerShader, "viewer.forwards"
        )
        self.viewerRightLocation = glGetUniformLocation(
            self.rayTracerShader, "viewer.right"
        )
        self.viewerUpLocation = glGetUniformLocation(
            self.rayTracerShader, "viewer.up"
        )
        self.sphereCountLocation = glGetUniformLocation(self.rayTracerShader, "sphereCount")
        self.planeCountLocation = glGetUniformLocation(self.rayTracerShader, "planeCount")
        self.lightCountLocation = glGetUniformLocation(self.rayTracerShader, "lightCount")
     
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
    
    def createColorBuffers(self):

        self.colorBuffers = []

        #for geometry pass
        self.gBuffer = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.gBuffer)

        self.g0Texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.g0Texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, self.screenWidth, self.screenHeight, 0, GL_RGBA, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, 
                            GL_TEXTURE_2D, self.g0Texture, 0)

        self.g1Texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.g1Texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, self.screenWidth, self.screenHeight, 0, GL_RGBA, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT1, 
                            GL_TEXTURE_2D, self.g1Texture, 0)

        self.g2Texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.g2Texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, self.screenWidth, self.screenHeight, 0, GL_RGBA, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT2, 
                            GL_TEXTURE_2D, self.g2Texture, 0)

        self.g3Texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.g3Texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, self.screenWidth, self.screenHeight, 0, GL_RGBA, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT3, 
                            GL_TEXTURE_2D, self.g3Texture, 0)

        glDrawBuffers(4, 
            (
                GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1, 
                GL_COLOR_ATTACHMENT2, GL_COLOR_ATTACHMENT3
            )
        )

        self.depthStencilBuffer = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, self.depthStencilBuffer)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, self.screenWidth, self.screenHeight)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, 
                                GL_RENDERBUFFER, self.depthStencilBuffer)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        #for raytracing shader
        self.colorBuffer = glGenTextures(1)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.colorBuffer)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, self.screenWidth, self.screenHeight, 0, GL_RGBA, GL_FLOAT, None)
    
    def createResourceMemory(self):

        """
            allocate storage for up to 1024 objects (why not?)
        """

        objectData = []

        # sphere: (cx cy cz r)  (r g b roughness) (- - - -)     (- - - -)             (- - - -)
        # plane:  (cx cy cz tx) (ty tz bx by)     (bz nx ny nz) (umin umax vmin vmax) (material_index - - -)
        # light:  (x y z s)     (r g b -)         (bz nx ny nz) (umin umax vmin vmax) (material_index - - -)
        for object in range(1024):
            for attribute in range(20):
                objectData.append(0.0)
        self.objectData = np.array(objectData, dtype=np.float32)

        self.objectDataTexture = glGenTextures(1)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.objectDataTexture)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA32F,5,1024,0,GL_RGBA,GL_FLOAT,bytes(self.objectData))
    
    def createMegaTexture(self):

        filenames = [
            "AlienArchitecture", "AlternatingColumnsConcreteTile", "BiomechanicalPlumbing", 
            "CarvedStoneFloorCheckered", "ChemicalStrippedConcrete", "ClayBrick",
            "CrumblingBrickWall", "DiamondSquareFlourishTiles", "EgyptianHieroglyphMetal"
        ]

        self.megaTexture = megatexture.MegaTexture(filenames)
    
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

        # sphere: (cx cy cz r) (r g b -) (- - - -) (- - - -) (- - - -)

        self.objectData[20*i]     = _sphere.center[0]
        self.objectData[20*i + 1] = _sphere.center[1]
        self.objectData[20*i + 2] = _sphere.center[2]

        self.objectData[20*i + 3] = _sphere.radius

        self.objectData[20*i + 4] = _sphere.color[0]
        self.objectData[20*i + 5] = _sphere.color[1]
        self.objectData[20*i + 6] = _sphere.color[2]

        self.objectData[20*i + 7] = _sphere.roughness
    
    def recordPlane(self, i, _plane):

        # plane: (cx cy cz tx) (ty tz bx by) (bz nx ny nz) (umin umax vmin vmax) (r g b -)

        self.objectData[20*i]     = _plane.center[0]
        self.objectData[20*i + 1] = _plane.center[1]
        self.objectData[20*i + 2] = _plane.center[2]

        self.objectData[20*i + 3] = _plane.tangent[0]
        self.objectData[20*i + 4] = _plane.tangent[1]
        self.objectData[20*i + 5] = _plane.tangent[2]

        self.objectData[20*i + 6] = _plane.bitangent[0]
        self.objectData[20*i + 7] = _plane.bitangent[1]
        self.objectData[20*i + 8] = _plane.bitangent[2]

        self.objectData[20*i + 9]  = _plane.normal[0]
        self.objectData[20*i + 10] = _plane.normal[1]
        self.objectData[20*i + 11] = _plane.normal[2]

        self.objectData[20*i + 12] = _plane.uMin
        self.objectData[20*i + 13] = _plane.uMax
        self.objectData[20*i + 14] = _plane.vMin
        self.objectData[20*i + 15] = _plane.vMax

        self.objectData[20*i + 16] = _plane.material_index
    
    def recordLight(self, i, _light):

        # light: (x y z s) (r g b -) (- - - -) (- - - -) (- - - -)

        self.objectData[20*i]     = _light.position[0]
        self.objectData[20*i + 1] = _light.position[1]
        self.objectData[20*i + 2] = _light.position[2]
        self.objectData[20*i + 3] = _light.strength

        self.objectData[20*i + 4] = _light.color[0]
        self.objectData[20*i + 5] = _light.color[1]
        self.objectData[20*i + 6] = _light.color[2]
    
    def updateScene(self, scene):

        scene.outDated = False

        glUseProgram(self.rayTracerShader)

        #spheres
        sphereCount = 0
        objectCount = 0
        for i,_sphere in enumerate(scene.spheres):
            self.recordSphere(i + sphereCount + objectCount, _sphere)
        sphereCount += len(scene.spheres)
        for room in scene.active_rooms:
            for i, _sphere in enumerate(room.spheres):
                self.recordSphere(i + sphereCount + objectCount, _sphere)
            sphereCount += len(room.spheres)
        glUniform1f(self.sphereCountLocation, sphereCount)
        objectCount += sphereCount

        #planes
        planeCount = 0
        for i,_plane in enumerate(scene.planes):
            self.recordPlane(i + planeCount + objectCount, _plane)
        planeCount += len(scene.planes)
        for room in scene.active_rooms:
            for i, _plane in enumerate(room.planes):
                self.recordPlane(i + planeCount + objectCount, _plane)
            planeCount += len(room.planes)
            for door in room.doors:
                for i,_plane in enumerate(door.planes):
                    self.recordPlane(i + planeCount + objectCount, _plane)
                planeCount += len(door.planes)
        glUniform1f(self.planeCountLocation, planeCount)
        objectCount += planeCount

        #lights
        lightCount = 0
        for i,_light in enumerate(scene.lights):
            self.recordLight(i + lightCount + objectCount, _light)
        lightCount += len(scene.lights)
        for room in scene.active_rooms:
            for i, _light in enumerate(room.lights):
                self.recordLight(i + lightCount + objectCount, _light)
            lightCount += len(room.lights)
        glUniform1f(self.lightCountLocation, lightCount)
        objectCount += lightCount

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.objectDataTexture)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA32F,5,1024,0,GL_RGBA,GL_FLOAT,bytes(self.objectData))
    
    def prepare_geometry_pass(self, scene):

        view_transform = pyrr.matrix44.create_look_at(
            eye = scene.camera.position,
            target = scene.camera.position + scene.camera.forwards,
            up = scene.camera.up,
            dtype = np.float32
        )

        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = 800/600, 
            near = 0.1, far = 20, dtype=np.float32
        )

        glUseProgram(self.shaderGPass)

        glUniformMatrix4fv(self.viewMatrixLocation, 1, False, view_transform)

        glUniformMatrix4fv(self.projectionMatrixLocation,1,GL_FALSE,projection_transform)

    def geometry_pass(self, scene):

        self.prepare_geometry_pass(scene)

        glUseProgram(self.shaderGPass)
        glBindFramebuffer(GL_FRAMEBUFFER, self.gBuffer)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glDrawBuffers(4, (
            GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1, 
            GL_COLOR_ATTACHMENT2, GL_COLOR_ATTACHMENT3
        ))
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.megaTexture.texture)

        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        glBindVertexArray(scene.vao)
        glDrawArrays(GL_TRIANGLES, 0, scene.vertexCount)
        for _room in scene.active_rooms:
            for _door in _room.doors:
                glBindVertexArray(_door.vao)
                glDrawArrays(GL_TRIANGLES, 0, _door.vertexCount)
            glBindVertexArray(_room.vao)
            glDrawArrays(GL_TRIANGLES, 0, _room.vertexCount)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
    
    def prepare_raytrace_pass(self, scene):

        glUseProgram(self.rayTracerShader)

        glUniform3fv(self.viewerPositionLocation, 1, scene.camera.position)
        glUniform3fv(self.viewerForwardsLocation, 1, scene.camera.forwards)
        glUniform3fv(self.viewerRightLocation, 1, scene.camera.right)
        glUniform3fv(self.viewerUpLocation, 1, scene.camera.up)

        glActiveTexture(GL_TEXTURE0)
        glBindImageTexture(0, self.colorBuffer, 0, GL_FALSE, 0, GL_WRITE_ONLY, GL_RGBA32F)
        glActiveTexture(GL_TEXTURE1)
        glBindImageTexture(1, self.objectDataTexture, 0, GL_FALSE, 0, GL_READ_ONLY, GL_RGBA32F)
        glActiveTexture(GL_TEXTURE3)
        glBindImageTexture(3, self.megaTexture.texture, 0, GL_FALSE, 0, GL_READ_ONLY, GL_RGBA32F)
        #g-Buffer
        glActiveTexture(GL_TEXTURE4)
        glBindImageTexture(4, self.g0Texture, 0, GL_FALSE, 0, GL_READ_ONLY, GL_RGBA32F)
        glActiveTexture(GL_TEXTURE5)
        glBindImageTexture(5, self.g1Texture, 0, GL_FALSE, 0, GL_READ_ONLY, GL_RGBA32F)
        glActiveTexture(GL_TEXTURE6)
        glBindImageTexture(6, self.g2Texture, 0, GL_FALSE, 0, GL_READ_ONLY, GL_RGBA32F)
        glActiveTexture(GL_TEXTURE7)
        glBindImageTexture(7, self.g3Texture, 0, GL_FALSE, 0, GL_READ_ONLY, GL_RGBA32F)

    def raytrace_pass(self, scene):

        self.prepare_raytrace_pass(scene)

        glUseProgram(self.rayTracerShader)
        glDispatchCompute(self.screenWidth, self.screenHeight, 1)
  
        # make sure writing to image has finished before read
        glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)
        glBindImageTexture(0, 0, 0, GL_FALSE, 0, GL_WRITE_ONLY, GL_RGBA32F)

    def drawScreen(self):
        glDisable(GL_CULL_FACE)
        glDisable(GL_DEPTH_TEST)
        glUseProgram(self.shader)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.colorBuffer)
        #glBindTexture(GL_TEXTURE_2D, self.g2Texture)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        pg.display.flip()

    def renderScene(self, scene):
        """
            Draw all objects in the scene
        """
        
        self.updateScene(scene)
        self.geometry_pass(scene)
        self.raytrace_pass(scene)
        self.drawScreen()
    
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