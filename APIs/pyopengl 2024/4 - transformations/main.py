from config import *
import mesh_factory
    
class App:


    def __init__(self):
        """ Initialise the program """

        self.initialize_glfw()
        self.initialize_opengl()

    def initialize_glfw(self) -> None:
        """
            Initialize all glfw related stuff. Make a window, basically.
        """
        glfw.init()
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR,3)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR,3)
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, 
            GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE
        )
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, 
            GLFW_CONSTANTS.GLFW_TRUE
        )
        self.window = glfw.create_window(
            SCREEN_WIDTH, SCREEN_HEIGHT, "Title", None, None)
        glfw.make_context_current(self.window)
    
    def initialize_opengl(self) -> None:
        """
            Initialize any opengl related stuff.
        """
        glClearColor(0.1, 0.2, 0.2, 1)

        #self.triangle_buffers, self.triangle_vao = mesh_factory.build_triangle_mesh()
        self.triangle_vbo, self.triangle_vao = mesh_factory.build_triangle_mesh2()
        self.quad_ebo, self.quad_vbo, self.quad_vao = mesh_factory.build_quad_mesh()
        self.shader = create_shader_program("shaders/vertex.txt", "shaders/fragment.txt")

    def run(self):
        """ Run the app """

        while not glfw.window_should_close(self.window):
            #check events
            if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_ESCAPE) \
                == GLFW_CONSTANTS.GLFW_PRESS:
                break
            glfw.poll_events()

            transform_1 = pyrr.matrix44.create_from_translation([-0.75, -0.75, 0.0], dtype=np.float32)

            transform_2 = pyrr.matrix44.create_from_z_rotation(glfw.get_time(), dtype=np.float32)

            transform_3 = pyrr.matrix44.create_from_translation([0.75, 0.75, 0.0], dtype=np.float32)
            
            transform = pyrr.matrix44.multiply(pyrr.matrix44.multiply(transform_1, transform_2), transform_3)

            #refresh screen
            glClear(GL_COLOR_BUFFER_BIT)
            #draw triangle
            glUseProgram(self.shader)
            location = glGetUniformLocation(self.shader, "model")
            glUniformMatrix4fv(location, 1, GL_FALSE, transform)
            #glBindVertexArray(self.triangle_vao)
            #glDrawArrays(GL_TRIANGLES, 0, 3)
            glBindVertexArray(self.quad_vao)
            glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_BYTE, ctypes.c_void_p(0))
            glfw.swap_buffers(self.window)

    def quit(self):
        """ cleanup the app, run exit code """

        #glDeleteBuffers(len(self.triangle_buffers), self.triangle_buffers)
        glDeleteBuffers(3, (self.triangle_vbo, self.quad_ebo, self.quad_vbo))
        glDeleteVertexArrays(2, (self.triangle_vao, self.quad_vao))
        glDeleteProgram(self.shader)
        glfw.destroy_window(self.window)
        glfw.terminate()

my_app = App()
my_app.run()
my_app.quit()