from config import *
import view

class TransformComponent:
    """ Represents a general object with a position and rotation applied """


    def __init__(self,
        position: list[float],
        eulers: list[float]):
        """
            Initialize a new entity

            Parameters:

                position: The position of the entity in the world (x,y,z)

                eulers: Angles (in degrees) representing rotations around the x,y,z axes.

        """

        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)

    def get_model_transform(self) -> np.ndarray:
        """
            Calculates and returns the entity's transform matrix,
            based on its position and rotation.
        """

        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)

        model_transform = pyrr.matrix44.multiply(
            m1=model_transform,
            m2=pyrr.matrix44.create_from_y_rotation(
                theta = np.radians(self.eulers[1]),
                dtype=np.float32
            )
        )

        model_transform = pyrr.matrix44.multiply(
            m1=model_transform,
            m2=pyrr.matrix44.create_from_z_rotation(
                theta = np.radians(self.eulers[2]),
                dtype=np.float32
            )
        )

        model_transform = pyrr.matrix44.multiply(
            m1=model_transform,
            m2=pyrr.matrix44.create_from_translation(
                vec=self.position,
                dtype=np.float32
            )
        )

        return model_transform

    def spin_by(self,
                d_theta: float,
                d_phi: float,
                phi_constraints = (-89, 89)) -> None:
        """
            Spin by the given amounts, in degrees.

            Parameters:

                d_theta: amount to spin around z axis

                d_phi: amount to spin around y axis

                phi_constraints: min and max angles for phi
        """

        self.eulers[1] = min(phi_constraints[1],
                        max(phi_constraints[0], self.eulers[1] + d_phi))

        self.eulers[2] = (self.eulers[2] + d_theta) % 360

    def spin_to_z(self, angle: float) -> None:
        """ Spin to the given angle, in degrees """

        self.eulers[2] = angle % 360

class FrameComponent:
    """ A frame of reference """

    global_up = np.array([0,0,1], dtype=np.float32)

    def __init__(self):
        """ Initialize a new frame of reference """

        self.up = np.array([0,0,1], dtype=np.float32)
        self.right = np.array([0,1,0], dtype=np.float32)
        self.forwards = np.array([1,0,0], dtype=np.float32)

    def update(self, eulers: np.ndarray) -> None:
        """ 
            Update the frame of reference to align its vectors
            with the given rotations.
        """

        eulers = np.radians(eulers)

        #calculate the forwards vector directly using spherical coordinates
        self.forwards = np.array(
            [
                np.cos(eulers[2]) * np.cos(eulers[1]),
                np.sin(eulers[2]) * np.cos(eulers[1]),
                np.sin(eulers[1])
            ], dtype=np.float32)
        self.right = pyrr.vector.normalise(np.cross(self.forwards, self.global_up))
        self.up = pyrr.vector.normalise(np.cross(self.right, self.forwards))

    def get_transform_to_local_space(self, pos: np.ndarray) -> np.ndarray:
        """ Get a matrix which will transform vertices
            into the local space of this frame of reference,
            placed at the given position."""

        return np.array((
            (self.right[0], self.up[0], -self.forwards[0], 0.),
            (self.right[1], self.up[1], -self.forwards[1], 0.),
            (self.right[2], self.up[2], -self.forwards[2], 0.),
            (-np.dot(self.right, pos), -np.dot(self.up, pos), np.dot(self.forwards, pos), 1.0)
        ), dtype = np.float32)

class LightComponent:
    """ A light. """


    def __init__(self, color: list[float], strength: float):
        """ Initializa a new light. """

        self.color = np.array(color, dtype=np.float32)
        self.strength = strength

class Cube:
    """ A spinning cube """


    def __init__(self, shader, material, position: list[float]):
        """ Initialize a new cube """

        self.shader = shader
        self.transform_component = TransformComponent(
            position = position,
            eulers = [0,0,0])
        self.material = material
        self.shader = shader

        glUseProgram(shader)
        # x, y, z, s, t, nx, ny, nz
        self.vertices = (
                -0.5, -0.5, -0.5, 0, 0, 0, 0, -1,
                -0.5,  0.5, -0.5, 1, 0, 0, 0, -1,
                 0.5,  0.5, -0.5, 1, 1, 0, 0, -1,

                 0.5,  0.5, -0.5, 1, 1, 0, 0, -1,
                 0.5, -0.5, -0.5, 0, 1, 0, 0, -1,
                -0.5, -0.5, -0.5, 0, 0, 0, 0, -1,

                 0.5,  0.5,  0.5, 0, 0, 0, 0,  1,
                -0.5,  0.5,  0.5, 1, 0, 0, 0,  1,
                -0.5, -0.5,  0.5, 1, 1, 0, 0,  1,

                -0.5, -0.5,  0.5, 1, 1, 0, 0,  1,
                 0.5, -0.5,  0.5, 0, 1, 0, 0,  1,
                 0.5,  0.5,  0.5, 0, 0, 0, 0,  1,

                -0.5, -0.5,  0.5, 1, 0, -1, 0,  0,
                -0.5,  0.5,  0.5, 1, 1, -1, 0,  0,
                -0.5,  0.5, -0.5, 0, 1, -1, 0,  0,

                -0.5,  0.5, -0.5, 0, 1, -1, 0,  0,
                -0.5, -0.5, -0.5, 0, 0, -1, 0,  0,
                -0.5, -0.5,  0.5, 1, 0, -1, 0,  0,

                 0.5, -0.5, -0.5, 1, 0, 1, 0,  0,
                 0.5,  0.5, -0.5, 1, 1, 1, 0,  0,
                 0.5,  0.5,  0.5, 0, 1, 1, 0,  0,

                 0.5,  0.5,  0.5, 0, 1, 1, 0,  0,
                 0.5, -0.5,  0.5, 0, 0, 1, 0,  0,
                 0.5, -0.5, -0.5, 1, 0, 1, 0,  0,

                 0.5, -0.5,  0.5, 0, 1, 0, -1,  0,
                -0.5, -0.5,  0.5, 1, 1, 0, -1,  0,
                -0.5, -0.5, -0.5, 1, 0, 0, -1,  0,

                -0.5, -0.5, -0.5, 1, 0, 0, -1,  0,
                 0.5, -0.5, -0.5, 0, 0, 0, -1,  0,
                 0.5, -0.5,  0.5, 0, 1, 0, -1,  0,

                 0.5,  0.5, -0.5, 0, 1, 0, 1,  0,
                -0.5,  0.5, -0.5, 1, 1, 0, 1,  0,
                -0.5,  0.5,  0.5, 1, 0, 0, 1,  0,

                -0.5,  0.5,  0.5, 1, 0, 0, 1,  0,
                 0.5,  0.5,  0.5, 0, 0, 0, 1,  0,
                 0.5,  0.5, -0.5, 0, 1, 0, 1,  0
            )
        self.vertex_count = len(self.vertices)//8
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))

        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))

    def draw(self, shader = None):
        self.transform_component.spin_to_z(20*(pg.time.get_ticks()/1000))
        model_transform = self.transform_component.get_model_transform()
        if shader is None:
            glUseProgram(self.shader)
            glUniformMatrix4fv(glGetUniformLocation(self.shader,"model"),1,GL_FALSE,model_transform)
        else:
            glUseProgram(shader)
            glUniformMatrix4fv(glGetUniformLocation(shader,"model"),1,GL_FALSE,model_transform)
        self.material.use()
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class skyBox:
    def __init__(self, model):
        self.model = model

    def draw(self,position, shader = None):
        self.model.draw(position, shader)

    def destroy(self):
        self.model.destroy()

class Player:
    """ A player """


    def __init__(self, position: list[float]):
        """ Initialize a new player """

        self.transform_component = TransformComponent(
            position = position,
            eulers = [0, 0, 0])
        self.frame_component = FrameComponent()
        self.move_speed = 1

    def move(self, direction: float, amount: float) -> None:
        """ Walk in the given direciton by the given amount """
        eulers: np.ndarray = self.transform_component.eulers
        pos: np.ndarray = self.transform_component.position
        direction = (direction + eulers[2]) % 360
        pos[0] += amount * self.move_speed * np.cos(np.radians(direction))
        pos[1] += amount * self.move_speed * np.sin(np.radians(direction))

    def increment_direction(self, theta_increase: float,
                                phi_increase: float) -> None:
        """ Spin the player around by the given angles """

        self.transform_component.spin_by(theta_increase, phi_increase)

    def update(self,shaders):

        pos = self.transform_component.position
        eulers = self.transform_component.eulers
        self.frame_component.update(eulers)
        lookat_matrix = self.frame_component.get_transform_to_local_space(pos)

        for shader in shaders:
            glUseProgram(shader)
            glUniformMatrix4fv(glGetUniformLocation(shader,"view"),1,GL_FALSE,lookat_matrix)
            glUniform3fv(glGetUniformLocation(shader,"cameraPos"),1, pos)

class Monkey:
    """ A cheeky monkey! """


    def __init__(self, position: list[float], model):
        """ Initialize a new monkey """

        self.transform_component = TransformComponent(
            position = position,
            eulers = [0, 0, 0])
        self.model = model

    def draw(self, outline, outlineColor, shader = None):
        self.model.draw(self.transform_component.position, outline, outlineColor, shader)

    def destroy(self):
        self.model.destroy()

class Ground:
    """ A piece of ground. """


    def __init__(self, position: list[float], model):
        """ Initialze a new piece of ground. """

        self.transform_component = TransformComponent(
            position = position, eulers = [0, 0, 0])
        self.model = model

    def draw(self, shader = None):
        self.model.draw(self.transform_component.position, False, None, shader)

    def destroy(self):
        self.model.destroy()

class PointLight:
    """ A pointlight. """


    def __init__(self, shaders, color: list[float],
                position: list[float], strength: float, index):
        """ Initialze a new PointLight """

        self.model = view.CubeBasic(shaders[0], 0.1, 0.1, 0.1, *color)
        self.light_component = LightComponent(color, strength)
        self.transform_component = TransformComponent(
            position = position, eulers = [0, 0, 0])
        self.shaders = []
        for i in range(1,len(shaders)):
            self.shaders.append(shaders[i])
        self.index = index

    def update(self) -> None:
        """ Update the light """
        position = self.transform_component.position
        color = self.light_component.color
        strength = self.light_component.strength

        for shader in self.shaders:
            glUseProgram(shader)
            glUniform3fv(glGetUniformLocation(shader, f"lights[{self.index}].pos"), 1, position)
            glUniform3fv(glGetUniformLocation(shader, f"lights[{self.index}].color"), 1, color)
            glUniform1f(glGetUniformLocation(shader, f"lights[{self.index}].strength"), strength)
            glUniform1i(glGetUniformLocation(shader, f"lights[{self.index}].enabled"), 1)

    def draw(self,shader = None):
        self.model.draw(self.transform_component.position, shader)

    def destroy(self):
        self.model.destroy()

class ParticleEmitter2DCreateInfo:
    """ Creation info for a 2D particle emitter """

    def __init__(self):
        self.pos = None
        self.color = None
        self.lifetime = None
        self.velocity_field = None
        self.size = None
        self.layer = None
        self.shader = None
        self.rate = None
        self.offset_function = None

class Particle2DCreateInfo:
    def __init__(self):
        self.pos = None
        self.color = None
        self.lifetime = None
        self.size = None
        self.layer = None
        self.shader = None

class Particle2D:
    def __init__(self, createInfo):
        self.pos = createInfo.pos
        self.color = createInfo.color
        self.lifetime = createInfo.lifetime
        self.size = createInfo.size
        self.layer = createInfo.layer
        self.shader = createInfo.shader
        self.t = 0

        self.vertex = [self.pos[0], self.pos[1], 0, 1]
        self.vertex = np.array(self.vertex, dtype=np.float32)
        glUseProgram(self.shader)
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, self.vertex.nbytes, self.vertex, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

    def update(self, velocity_field):
        glUseProgram(self.shader)
        self.t += 1
        velocity = velocity_field(self.pos)
        self.pos[0] += velocity[0] / (100 * self.layer)
        self.pos[1] += velocity[1] / (100 * self.layer)
        self.vertex[0] = self.pos[0]
        self.vertex[1] = self.pos[1]
        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, self.vertex.nbytes, self.vertex, GL_STATIC_DRAW)

    def draw(self):
        glUseProgram(self.shader)
        color = np.array([self.color[0], self.color[1], self.color[2], max(1 - self.t/self.lifetime, 0)], dtype=np.float32)
        glUniform4fv(glGetUniformLocation(self.shader, "object_color"), 1, color)
        glUniform1f(glGetUniformLocation(self.shader, "size"), self.size)
        glUniform1f(glGetUniformLocation(self.shader, "layer"), self.layer)
        glBindVertexArray(self.VAO)
        glDrawArrays(GL_POINTS, 0, 1)

    def should_destroy(self):
        return self.t >= self.lifetime

    def destroy(self):
        glDeleteVertexArrays(1, (self.VAO,))
        glDeleteBuffers(1, (self.VBO,))

class ParticleEmitter2D:
    def __init__(self, createInfo):
        self.pos = createInfo.pos
        self.color = createInfo.color
        self.lifetime = createInfo.lifetime
        self.velocity_field = createInfo.velocity_field
        self.size = createInfo.size
        self.layer = createInfo.layer
        self.shader = createInfo.shader
        self.rate = createInfo.rate
        self.offset_function = createInfo.offset_function
        self.particles = []
        self.t = 0
    
    def update(self):
        #create new particles
        self.t += self.rate
        while (self.t > 1):
            self.t -= 1
            createInfo = Particle2DCreateInfo()
            createInfo.size = self.size
            createInfo.color = self.color
            createInfo.layer = self.layer
            offset = self.offset_function()
            createInfo.pos = [self.pos[0] + offset[0], self.pos[1] + offset[1]]
            createInfo.shader = self.shader
            createInfo.lifetime = self.lifetime
            self.particles.append(Particle2D(createInfo))
        
        #update existing particles
        for particle in self.particles:
            particle.update(self.velocity_field)
        
        #check for deletion
        for particle in self.particles:
            if (particle.should_destroy()):
                self.particles.pop(self.particles.index(particle))
                particle.destroy()

    def draw(self):
        for particle in self.particles:
            particle.draw()

    def destroy(self):
        for particle in self.particles:
            particle.destroy()
        self.particles = []

class Scene:


    def __init__(self, shaders, monkey_model, ground_model, skybox_model, wood_texture):

        shader3DTextured = shaders[0]
        shader3DColored = shaders[1]
        shader3DBillboard = shaders[6]

        self.monkey = Monkey(np.array([0,0,0],dtype=np.float32), monkey_model)
        self.cube = Cube(shader3DTextured, wood_texture,[1,1,0.5])
        self.player = Player([0,0,1.2])
        self.lightCount = 0
        self.light = PointLight([shader3DColored, shader3DTextured,shader3DBillboard], [0.2, 0.7, 0.8], [1,1.7,1.5], 2, self.lightCount)
        self.lightCount += 1
        self.light2 = PointLight([shader3DColored, shader3DTextured, shader3DBillboard], [0.9, 0.4, 0.0], [0,1.7,0.5], 2, self.lightCount)
        self.lightCount += 1
        self.ground = Ground(np.array([0,0,0],dtype=np.float32), ground_model)
        self.skyBox = skyBox(skybox_model)

    def update(self, shaders):
        
        self.light.update()
        self.light2.update()
        self.player.update(shaders)

    def move_player(self, direction: float, amount: float) -> None:
        self.player.move(direction, amount)

    def spin_player(self, theta_increment: float, phi_increment: float) -> None:
        self.player.increment_direction(theta_increment, phi_increment)

    def destroy(self):
        self.monkey.destroy()
        self.cube.destroy()
        self.light.destroy()
        self.light2.destroy()
        self.cube.destroy()
        self.ground.destroy()
        self.skyBox.destroy()
