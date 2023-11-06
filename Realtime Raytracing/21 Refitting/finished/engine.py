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
        """
        self.colorBuffer = materials.MaterialFixed(
            width = self.screenWidth, 
            height = self.screenHeight)
        """

        sphere_count = int(len(_scene.spheres))
        self.sphereBuffer = buffer.Buffer(
            size = sphere_count, binding = 1, dtype=data_type_sphere)
        self.nodeBuffer = buffer.Buffer(
            size = len(_scene.nodes), binding = 2, dtype=data_type_bvh_node)
        self.indexBuffer = buffer.Buffer(
            size = len(_scene.sphere_ids), binding = 3, dtype=np.int32)
        self.materialBuffer = buffer.Buffer(
            size = len(_scene.materials), binding = 4, dtype=data_type_material)

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
        
        self.sphereBuffer.blit(scene.spheres)
        
        self.nodeBuffer.blit(scene.nodes)

        self.indexBuffer.blit(scene.sphere_ids)

        self.materialBuffer.blit(scene.materials)

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
        
        self.sphereBuffer.readFrom()
        self.nodeBuffer.readFrom()
        self.indexBuffer.readFrom()
        self.materialBuffer.readFrom()

        self.skyBoxMaterial.use()
        
    def renderScene(self, scene: scene.Scene):
        """
            Draw all objects in the scene
        """
        
        start = time.time()
        glUseProgram(self.rayTracerShader)

        self.prepareScene(scene)

        self.colorBuffer.writeTo()
        
        subgroup_x_count = int(self.colorBuffer.sizes[self.colorBuffer.detailLevel] / 8)
        subgroup_y_count = int(self.colorBuffer.sizes[self.colorBuffer.detailLevel] / 8)

        glDispatchCompute(subgroup_x_count, subgroup_y_count, 1)
        
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