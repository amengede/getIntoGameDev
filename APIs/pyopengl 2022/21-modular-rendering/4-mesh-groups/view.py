from config import *
from view_constants import *
from shader_constants import *
import buffer
import model
from shaders import *
from framebuffers import *
from materials import *
from meshes import *

class GraphicsEngine:
    """
        Renders stuff!
    """

    def __init__(self, width: int, height: int,
                 window: "glfw.Window"):
        """
        Initialize the graphics engine.

        Parameters:

            width: width of the application window

            height: height of the application window

            window: the application window
        """

        self.width = width
        self.height = height
        self.window = window

        self.set_up_opengl()

        self.create_assets()

        self.create_framebuffers()

        self.setup_shaders()

    def set_up_opengl(self) -> None:
        """
            Set up Initial OpenGL configuration.
        """

        glClearColor(0.0, 0.0, 0.0, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_PROGRAM_POINT_SIZE)

    def create_framebuffers(self) -> None:
        """
            Create framebuffers for the program to write to.
        """
        self.screen_framebuffer = Framebuffer(self.width, self.height,
                                              offscreen=False)
        self.framebuffers = []
        for i in range(2):
            framebuffer = Framebuffer(self.width, self.height)
            framebuffer.add_color_attachment()
            framebuffer.add_color_attachment()
            framebuffer.add_depth_stencil_attachment()
            self.framebuffers.append(framebuffer)

    def setup_shaders(self) -> None:
        """
            Create and configure shaders for the program to render with.
        """

        self.shaders: dict[int, Shader] = {}

        for pipeline_type in SHADERS:
            shader = Shader(pipeline_type)
            shader.use()
            self.shaders[pipeline_type] = shader

        # Set one-time uniforms
        projection = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = self.width/self.height,
            near = 0.1, far = 50, dtype=np.float32
        )

        pipeline_type = PIPELINE_TYPE_LIT
        shader = self.shaders[pipeline_type]
        shader.use()
        shader.bind_mat4(UNIFORM_TYPE_PROJECTION, projection)
        shader.bind_int(UNIFORM_TYPE_ALBEDO, 0)
        shader.bind_int(UNIFORM_TYPE_AMBIENT_OCCLUSION, 1)
        shader.bind_int(UNIFORM_TYPE_SPECULAR, 2)
        shader.bind_int(UNIFORM_TYPE_NORMAL, 3)
        shader.bind_float(UNIFORM_TYPE_MATERIAL_COUNT,
                          len(ADVANCED_MATERIAL_FILENAMES))

        pipeline_type = PIPELINE_TYPE_PARTICLE
        shader = self.shaders[pipeline_type]
        shader.use()
        shader.bind_mat4(UNIFORM_TYPE_PROJECTION, projection)

        pipeline_type = PIPELINE_TYPE_UNLIT
        shader = self.shaders[pipeline_type]
        shader.use()
        shader.bind_mat4(UNIFORM_TYPE_PROJECTION, projection)
        shader.bind_int(UNIFORM_TYPE_MATERIAL, 0)
        shader.bind_float(UNIFORM_TYPE_MATERIAL_COUNT,
                          len(SIMPLE_MATERIAL_FILENAMES))

        pipeline_type = PIPELINE_TYPE_SCREEN
        shader = self.shaders[pipeline_type]
        shader.use()
        shader.bind_int(UNIFORM_TYPE_MATERIAL, 0)

        pipeline_type = PIPELINE_TYPE_BLOOM_BLUR
        shader = self.shaders[pipeline_type]
        shader.use()
        shader.bind_int(UNIFORM_TYPE_MATERIAL, 0)
        shader.bind_int(UNIFORM_TYPE_BRIGHT_MATERIAL, 1)

        pipeline_type = PIPELINE_TYPE_BLOOM_TRANSFER
        shader = self.shaders[pipeline_type]
        shader.use()
        shader.bind_int(UNIFORM_TYPE_MATERIAL, 0)
        shader.bind_int(UNIFORM_TYPE_BRIGHT_MATERIAL, 1)

        pipeline_type = PIPELINE_TYPE_BLOOM_RESOLVE
        shader = self.shaders[pipeline_type]
        shader.use()
        shader.bind_int(UNIFORM_TYPE_MATERIAL, 0)
        shader.bind_int(UNIFORM_TYPE_BRIGHT_MATERIAL, 1)

    def create_assets(self) -> None:
        """
            Create all the assets used for rendering.
        """

        self.create_meshes()

        self.create_materials()

    def create_meshes(self) -> None:
        """
            Load and conglomerate all meshes.
        """

        self.mesh_group = MeshGroup()
        for mesh_type, filename in FULL_ATTRIBUTE_FILENAMES.items():
            self.mesh_group.add_mesh_from_file(mesh_type, filename)

        for mesh_type, size in FULL_ATTRIBUTE_BILLBOARDS.items():
            self.mesh_group.add_billboard(mesh_type, size)
        
        self.mesh_group.build()

    def create_materials(self) -> None:
        """
            Create all the materials used by the engine.
        """

        self.material_groups:dict[int, MaterialGroup] = {}

        material_group = MaterialGroup()
        material_group.add_texture_array(SIMPLE_MATERIAL_FILENAMES, "")
        self.material_groups[PIPELINE_TYPE_UNLIT] = material_group

        material_group = MaterialGroup()
        material_group.add_texture_array(ADVANCED_MATERIAL_FILENAMES, "_albedo")
        material_group.add_texture_array(ADVANCED_MATERIAL_FILENAMES, "_ao")
        material_group.add_texture_array(ADVANCED_MATERIAL_FILENAMES, "_glossmap")
        material_group.add_texture_array(ADVANCED_MATERIAL_FILENAMES, "_normal")
        self.material_groups[PIPELINE_TYPE_LIT] = material_group

        self.screen = TexturedQuad(0, 0, 1, 1)

        self.font = Font()
        self.fps_label = TextLine("FPS: ", self.font, (-0.9, 0.9), (0.05, 0.05))

    def update_fps(self, new_fps: int) -> None:
        """
            Rebuild the text label to reflect the given framerate.
        """

        self.fps_label.build(f"FPS: {new_fps}")

    def render_scene_objects(self, scene: model.Scene) -> None:
        """
            Render all the "3D world" objects.
        """

        view_transform = scene.player.camera.matrix
        view_position = scene.player.transform.position

        self.framebuffers[0].draw_to()

        glDrawBuffers(2, (GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1))
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

        pipeline_type = PIPELINE_TYPE_LIT
        shader = self.shaders[pipeline_type]
        shader.use()

        shader.bind_mat4(UNIFORM_TYPE_VIEW, view_transform)
        shader.bind_vec3(UNIFORM_TYPE_CAMERA_POS, view_position)

        self.material_groups[pipeline_type].bind()

        for i,light in enumerate(scene.lights):
            transform_component: model.TransformComponent = light.transform
            position = transform_component.position
            light_component: model.LightComponent = light.light
            color = light_component.color
            strength = light_component.strength

            shader.bind_vec3(UNIFORM_TYPE_LIGHT0_POS + 3 * i, position)
            shader.bind_vec3(UNIFORM_TYPE_LIGHT0_COLOR + 3 * i, color)
            shader.bind_float(UNIFORM_TYPE_LIGHT0_STRENGTH + 3 * i, strength)

        self.mesh_group.bind()

        for obj in scene.lit_objects:
            render_component: model.RenderComponent = obj.render
            mesh_type = render_component.mesh_type
            material_type = render_component.material_type - WOOD_MATERIAL
            transform_component: model.TransformComponent = obj.transform
            model_matrix = transform_component.matrix

            shader.bind_float(UNIFORM_TYPE_MATERIAL_INDEX, material_type)
            shader.bind_mat4(UNIFORM_TYPE_MODEL, model_matrix)

            self.mesh_group.draw(mesh_type)

        pipeline_type = PIPELINE_TYPE_UNLIT
        shader = self.shaders[pipeline_type]
        shader.use()

        shader.bind_mat4(UNIFORM_TYPE_VIEW, view_transform)

        self.material_groups[pipeline_type].bind()

        for obj in scene.unlit_objects:
            render_component: model.RenderComponent = obj.render
            mesh_type = render_component.mesh_type
            material_type = render_component.material_type - WOOD_MATERIAL
            transform_component: model.TransformComponent = obj.transform
            model_matrix = transform_component.matrix
            light_component: model.LightComponent = obj.light
            color = light_component.color

            shader.bind_float(UNIFORM_TYPE_MATERIAL_INDEX, material_type)
            shader.bind_vec3(UNIFORM_TYPE_TINT, color)
            shader.bind_mat4(UNIFORM_TYPE_MODEL, model_matrix)

            self.mesh_group.draw(mesh_type)

        pipeline_type = PIPELINE_TYPE_PARTICLE
        shader = self.shaders[pipeline_type]
        shader.use()

        shader.bind_mat4(UNIFORM_TYPE_VIEW, view_transform)

        glBindVertexArray(scene.particles.VAO)
        glDrawArrays(GL_POINTS, 0, scene.particles.particle_count)

    def render(self, scene: model.Scene) -> None:
        """
            Render the given scene.
        """

        self.render_scene_objects(scene)

        #Post processing pass
        pipeline_type = PIPELINE_TYPE_SCREEN
        shader = self.shaders[pipeline_type]
        shader.use()
        self.framebuffers[0].draw_to()
        glDrawBuffers(2, (GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1))
        glDisable(GL_DEPTH_TEST)

        #Bloom
        for _ in range(8):

            self.framebuffers[1].draw_to()
            glDrawBuffers(1, (GL_COLOR_ATTACHMENT1,))
            glDisable(GL_DEPTH_TEST)

            pipeline_type = PIPELINE_TYPE_BLOOM_BLUR
            shader = self.shaders[pipeline_type]
            shader.use()
            self.framebuffers[0].read_from()
            glBindVertexArray(self.screen.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.screen.vertex_count)

            self.framebuffers[0].draw_to()
            glDrawBuffers(1, (GL_COLOR_ATTACHMENT1,))
            glDisable(GL_DEPTH_TEST)

            pipeline_type = PIPELINE_TYPE_BLOOM_TRANSFER
            shader = self.shaders[pipeline_type]
            shader.use()
            self.framebuffers[1].read_from()
            glBindVertexArray(self.screen.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.screen.vertex_count)

        self.framebuffers[1].draw_to()
        glDrawBuffers(1, (GL_COLOR_ATTACHMENT0,))

        pipeline_type = PIPELINE_TYPE_BLOOM_RESOLVE
        shader = self.shaders[pipeline_type]
        shader.use()
        self.framebuffers[0].read_from()
        glBindVertexArray(self.screen.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.screen.vertex_count)

        pipeline_type = PIPELINE_TYPE_SCREEN
        shader = self.shaders[pipeline_type]
        shader.use()
        shader.bind_vec4(UNIFORM_TYPE_TINT,
                         np.array([1.0, 0.0, 0.0, 1.0], dtype = np.float32))
        self.font.use()
        glBindVertexArray(self.fps_label.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.fps_label.vertex_count)

        #CRT emulation pass
        pipeline_type = PIPELINE_TYPE_CRT
        shader = self.shaders[pipeline_type]
        shader.use()
        self.framebuffers[0].draw_to()
        glDrawBuffers(1, (GL_COLOR_ATTACHMENT0,))
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_DEPTH_TEST)

        self.framebuffers[1].read_from()
        glBindVertexArray(self.screen.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.screen.vertex_count)

        #Put the final result on screen
        pipeline_type = PIPELINE_TYPE_SCREEN
        shader = self.shaders[pipeline_type]
        shader.use()
        self.screen_framebuffer.draw_to()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_DEPTH_TEST)

        shader.bind_vec4(UNIFORM_TYPE_TINT,
                         np.array([1.0, 1.0, 1.0, 1.0], dtype = np.float32))
        self.framebuffers[0].read_from()
        glBindVertexArray(self.screen.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.screen.vertex_count)

        #For uncapped framerate: glFlush
        glfw.swap_buffers(self.window)
        #glFlush()

    def destroy(self) -> None:
        """
            Destroy everything.
        """

        self.mesh_group.destroy()
        self.screen.destroy()
        for material_group in self.material_groups.values():
            material_group.destroy()
        self.font.destroy()
        self.fps_label.destroy()
        for shader in self.shaders.values():
            shader.destroy()
        for framebuffer in self.framebuffers:
            framebuffer.destroy()
        glfw.destroy_window(self.window)
