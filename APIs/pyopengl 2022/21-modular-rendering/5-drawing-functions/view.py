from config import *
from view_constants import *
from shader_constants import *
import buffer
import model
from shaders import *
from framebuffers import *
from materials import *
from meshes import *

class RenderPass:
    """
        Describes the resources that will be touched by a set of rendering
        operations.
    """

    def __init__(self, depth_enabled: bool, clear_depth: bool, clear_color: bool):

        self.has_depth_test = depth_enabled
        self.clear_mask = 0
        if clear_depth:
            self.clear_mask |= GL_DEPTH_BUFFER_BIT
        if clear_color:
            self.clear_mask |= GL_COLOR_BUFFER_BIT
        self.draw_targets = []

    def add_framebuffer(self, framebuffer: Framebuffer) -> "RenderPass":

        self.framebuffer = framebuffer
        return self

    def add_draw_target(self, target: int) -> "RenderPass":

        self.draw_targets.append(target)
        return self

    def begin(self) -> None:

        self.framebuffer.draw_to()
        glDrawBuffers(len(self.draw_targets), self.draw_targets)
        glClear(self.clear_mask)
        if self.has_depth_test:
            glEnable(GL_DEPTH_TEST)
        else:
            glDisable(GL_DEPTH_TEST)

def post_renderpass(shader: int,
                    src: Framebuffer,
                    dst: Framebuffer) -> None:

    dst.draw_to()
    shader.use()
    src.read_from()
    glDrawArrays(GL_TRIANGLES, 0, 6)

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

        self.create_renderpasses()

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

    def create_renderpasses(self) -> None:
        """
            Create renderpasses
        """

        self.scene_renderpass = RenderPass(depth_enabled = True,
            clear_depth = True,
            clear_color = True)\
            .add_framebuffer(self.framebuffers[0])\
            .add_draw_target(GL_COLOR_ATTACHMENT0)\
            .add_draw_target(GL_COLOR_ATTACHMENT1)

        self.bloom_renderpasses = [
            RenderPass(depth_enabled = False,
                clear_depth = False,
                clear_color = False)\
            .add_framebuffer(self.framebuffers[0])\
            .add_draw_target(GL_COLOR_ATTACHMENT1),

            RenderPass(depth_enabled = False,
                clear_depth = False,
                clear_color = False)\
            .add_framebuffer(self.framebuffers[1])\
            .add_draw_target(GL_COLOR_ATTACHMENT1)
        ]

        self.post_renderpasses = [
            RenderPass(depth_enabled = False,
                clear_depth = False,
                clear_color = False)\
            .add_framebuffer(self.framebuffers[0])\
            .add_draw_target(GL_COLOR_ATTACHMENT0),

            RenderPass(depth_enabled = False,
                clear_depth = False,
                clear_color = False)\
            .add_framebuffer(self.framebuffers[1])\
            .add_draw_target(GL_COLOR_ATTACHMENT0)
        ]

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

        self.scene_renderpass.begin()

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
        glBindVertexArray(self.screen.vao)

        #Bloom
        for renderpass in self.bloom_renderpasses:
            renderpass.begin()
        for _ in range(8):

            post_renderpass(self.shaders[PIPELINE_TYPE_BLOOM_BLUR],
                            src=self.framebuffers[0],
                            dst=self.framebuffers[1])

            post_renderpass(self.shaders[PIPELINE_TYPE_BLOOM_TRANSFER],
                            src=self.framebuffers[1],
                            dst=self.framebuffers[0])

        for renderpass in self.post_renderpasses:
            renderpass.begin()

        post_renderpass(self.shaders[PIPELINE_TYPE_BLOOM_RESOLVE],
                        src=self.framebuffers[0],
                        dst=self.framebuffers[1])

        # FPS Label
        pipeline_type = PIPELINE_TYPE_SCREEN
        shader = self.shaders[pipeline_type]
        shader.use()
        shader.bind_vec4(UNIFORM_TYPE_TINT,
                         (1.0, 0.0, 0.0, 1.0))
        self.font.use()
        glBindVertexArray(self.fps_label.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.fps_label.vertex_count)
        shader.bind_vec4(UNIFORM_TYPE_TINT,
                         (1.0, 1.0, 1.0, 1.0))
        glBindVertexArray(self.screen.vao)

        # CRT Emulation
        post_renderpass(self.shaders[PIPELINE_TYPE_CRT],
                        src=self.framebuffers[1],
                        dst=self.framebuffers[0])

        #Put the final result on screen
        post_renderpass(self.shaders[PIPELINE_TYPE_SCREEN],
                        src=self.framebuffers[0],
                        dst=self.screen_framebuffer)

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
