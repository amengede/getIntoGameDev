from config import *
import scene
import sphere
import node
import materials
import screen_quad
import buffer

class Engine:
    """
        Responsible for drawing scenes
    """

    def __init__(self, width, height, _scene: scene.Scene):
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

        self.makeAssets(_scene)
        
        self.framesRendered = 0
        self.numFrames = 0
    
    def makeAssets(self, _scene: scene.Scene) -> None:
        """ Make all the stuff. """

        self.screenQuad = screen_quad.ScreenQuad()
        self.colorBuffer = materials.Material(minDetail = 8, maxDetail = 1024)

        self.triangleBuffer = buffer.Buffer(size = len(_scene.triangles), binding = 1, floatCount = 16, dtype=np.float32)
        self.nodeBuffer = buffer.Buffer(size = _scene.nodes_used, binding = 2, floatCount = 8, dtype=np.float32)
        self.indexBuffer = buffer.Buffer(size = len(_scene.ids), binding = 3, floatCount = 1, dtype=np.int32)

        self.shader = self.createShader("shaders/frameBufferVertex.txt",
                                        "shaders/frameBufferFragment.txt")
        
        self.rayTracerShader = self.createComputeShader("shaders/rayTracer.txt")

        self.skyBoxMaterial = materials.CubeMapMaterial("gfx/sky")
        glUseProgram(self.rayTracerShader)
        glUniform1i(glGetUniformLocation(self.rayTracerShader, "sky_cube"), 4)
    
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

    def updateScene(self, scene: scene.Scene):

        scene.outDated = False

        glUseProgram(self.rayTracerShader)

        for i,_triangle in enumerate(scene.triangles):
            self.triangleBuffer.recordTriangle(i, _triangle)

        for i in range(scene.nodes_used):
            _node = scene.nodes[i]
            if _node.min_corner is not None:
                self.nodeBuffer.recordNode(i, _node)

        for i,_index in enumerate(scene.ids):
            self.indexBuffer.recordSphereIndex(i, _index)

    def prepareScene(self, scene: scene.Scene):
        """
            Send scene data to the shader.
        """

        glUseProgram(self.rayTracerShader)

        correction_factor = self.screenHeight / self.screenWidth

        glUniform3fv(glGetUniformLocation(self.rayTracerShader, "viewer.position"), 1, scene.camera.position)
        glUniform3fv(glGetUniformLocation(self.rayTracerShader, "viewer.forwards"), 1, scene.camera.forwards)
        glUniform3fv(glGetUniformLocation(self.rayTracerShader, "viewer.right"), 1, scene.camera.right)
        glUniform3fv(glGetUniformLocation(self.rayTracerShader, "viewer.up"), 1, correction_factor * scene.camera.up)

        if scene.outDated:
            self.updateScene(scene)
        
        self.triangleBuffer.readFrom()
        self.nodeBuffer.readFrom()
        self.indexBuffer.readFrom()

        self.skyBoxMaterial.use()
        
    def renderScene(self, scene: scene.Scene):
        """
            Draw all objects in the scene
        """
        
        start = time.time()
        glUseProgram(self.rayTracerShader)

        self.prepareScene(scene)

        self.colorBuffer.writeTo()
        
        subgroup_count = int(self.colorBuffer.sizes[self.colorBuffer.detailLevel] / 8)

        glDispatchCompute(subgroup_count, subgroup_count, 1)
        glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)

        self.drawScreen()
        finish = time.time()
        #print(f"render took {(finish - start) * 1000} milliseconds.")

    def drawScreen(self):
        glUseProgram(self.shader)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        self.colorBuffer.readFrom()
        self.screenQuad.draw()
        glFlush()
        self.numFrames += 1
    
    def adaptResolution(self, frameRate):

        if frameRate > self.targetFrameRate + self.frameRateMargin:
            #increase resolution
            self.colorBuffer.upsize()
        elif frameRate < self.targetFrameRate - self.frameRateMargin:
            #reduce resolution
            self.colorBuffer.downsize()
    
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