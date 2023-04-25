from config import *
import screen_quad
import material
import scene

class Engine:
    """
        Responsible for drawing scenes
    """

    def __init__(self, width: int, height: int):
        """
            Initialize a flat raytracing context
            
                Parameters:
                    width (int): width of screen
                    height (int): height of screen
        """
        self.screenWidth = width
        self.screenHeight = height

        self.makeAssets()
    
    def makeAssets(self) -> None:
        """ Make all the stuff. """

        self.screenQuad = screen_quad.ScreenQuad()

        self.colorBuffer = material.Material(self.screenWidth, self.screenHeight)

        self.shader = self.createShader("shaders/frameBufferVertex.txt",
                                        "shaders/frameBufferFragment.txt")
        
        self.rayTracerShader = self.createComputeShader("shaders/rayTracer.txt")
    
    def createShader(self, vertexFilepath, fragmentFilepath) -> int:
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
    
    def createComputeShader(self, filepath) -> int:
        """
            Read source code, compile and link shaders.
            Returns the compiled and linked program.
        """

        with open(filepath,'r') as f:
            compute_src = f.readlines()
        
        shader = compileProgram(compileShader(compute_src, GL_COMPUTE_SHADER))
        
        return shader

    def prepareScene(self, _scene: scene.Scene) -> None:
        """
            Send scene data to the shader.
        """

        glUseProgram(self.rayTracerShader)

        glUniform3fv(glGetUniformLocation(self.rayTracerShader, "viewer.position"), 1, _scene.camera.position)
        glUniform3fv(glGetUniformLocation(self.rayTracerShader, "viewer.forwards"), 1, _scene.camera.forwards)
        glUniform3fv(glGetUniformLocation(self.rayTracerShader, "viewer.right"), 1, _scene.camera.right)
        glUniform3fv(glGetUniformLocation(self.rayTracerShader, "viewer.up"), 1, _scene.camera.up)

        glUniform1f(glGetUniformLocation(self.rayTracerShader, "sphereCount"), len(_scene.spheres))

        for i,_sphere in enumerate(_scene.spheres):
            glUniform3fv(glGetUniformLocation(self.rayTracerShader, f"spheres[{i}].center"), 1, _sphere.center)
            glUniform1f(glGetUniformLocation(self.rayTracerShader, f"spheres[{i}].radius"), _sphere.radius)
            glUniform3fv(glGetUniformLocation(self.rayTracerShader, f"spheres[{i}].color"), 1, _sphere.color)
        
    def renderScene(self, _scene: scene.Scene) -> None:
        """
            Draw all objects in the scene
        """
        
        glUseProgram(self.rayTracerShader)

        self.prepareScene(_scene)

        self.colorBuffer.writeTo()
        
        glDispatchCompute(int(self.screenWidth/8), int(self.screenHeight/8), 1)
  
        # make sure writing to image has finished before read
        glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)

        self.drawScreen()

    def drawScreen(self) -> None:
        glUseProgram(self.shader)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        self.colorBuffer.readFrom()
        self.screenQuad.draw()
        pg.display.flip()
    
    def destroy(self) -> None:
        """
            Free any allocated memory
        """
        glDeleteProgram(self.rayTracerShader)
        self.screenQuad.destroy()
        self.colorBuffer.destroy()
        glDeleteProgram(self.shader)