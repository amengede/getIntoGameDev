from config import *
import view

class Cube:
    def __init__(self, shader, material, position):
        self.material = material
        self.shader = shader
        self.position = position
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
        angle = np.radians((20*(pg.time.get_ticks()/1000))%360)
        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        model_transform = pyrr.matrix44.multiply(model_transform, pyrr.matrix44.create_from_z_rotation(theta=angle,dtype=np.float32))
        model_transform = pyrr.matrix44.multiply(model_transform, pyrr.matrix44.create_from_translation(vec=np.array(self.position),dtype=np.float32))
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
    def __init__(self, position):
        self.position = np.array(position,dtype=np.float32)
        self.forward = np.array([0, 0, 0],dtype=np.float32)
        self.theta = 0
        self.phi = 0
        self.moveSpeed = 1
        self.global_up = np.array([0, 0, 1], dtype=np.float32)

    def move(self, direction, amount):
        walkDirection = (direction + self.theta) % 360
        self.position[0] += amount * self.moveSpeed * np.cos(np.radians(walkDirection),dtype=np.float32)
        self.position[1] += amount * self.moveSpeed * np.sin(np.radians(walkDirection),dtype=np.float32)

    def increment_direction(self, theta_increase, phi_increase):
        self.theta = (self.theta + theta_increase) % 360
        self.phi = min(max(self.phi + phi_increase,-89),89)

    def update(self,shaders):
        camera_cos = np.cos(np.radians(self.theta),dtype=np.float32)
        camera_sin = np.sin(np.radians(self.theta),dtype=np.float32)
        camera_cos2 = np.cos(np.radians(self.phi),dtype=np.float32)
        camera_sin2 = np.sin(np.radians(self.phi),dtype=np.float32)
        self.forward[0] = camera_cos * camera_cos2
        self.forward[1] = camera_sin * camera_cos2
        self.forward[2] = camera_sin2
        
        right = pyrr.vector3.cross(self.global_up,self.forward)
        up = pyrr.vector3.cross(self.forward,right)
        lookat_matrix = pyrr.matrix44.create_look_at(self.position, self.position + self.forward, up,dtype=np.float32)
        for shader in shaders:
            glUseProgram(shader)
            glUniformMatrix4fv(glGetUniformLocation(shader,"view"),1,GL_FALSE,lookat_matrix)
            glUniform3fv(glGetUniformLocation(shader,"cameraPos"),1,self.position)

class Monkey:
    def __init__(self, position, model):
        self.model = model
        self.position = position

    def draw(self, shader = None):
        self.model.draw(self.position,shader)

    def destroy(self):
        self.model.destroy()

class Ground:
    def __init__(self, position, model):
        self.model = model
        self.position = position

    def draw(self,shader = None):
        self.model.draw(self.position,shader)

    def destroy(self):
        self.model.destroy()

class Light:
    def __init__(self, shaders, colour, position, strength, index):
        self.model = view.CubeBasic(shaders[0], 0.1, 0.1, 0.1, colour[0], colour[1], colour[2])
        self.colour = np.array(colour, dtype=np.float32)
        self.shaders = []
        for i in range(1,len(shaders)):
            self.shaders.append(shaders[i])
        self.position = np.array(position, dtype=np.float32)
        self.strength = strength
        self.index = index

    def update(self):
        for shader in self.shaders:
            glUseProgram(shader)
            glUniform3fv(glGetUniformLocation(shader,f"lights[{self.index}].pos"),1,self.position)
            glUniform3fv(glGetUniformLocation(shader,f"lights[{self.index}].color"),1,self.colour)
            glUniform1f(glGetUniformLocation(shader,f"lights[{self.index}].strength"),self.strength)
            glUniform1i(glGetUniformLocation(shader,f"lights[{self.index}].enabled"),1)

    def draw(self,shader = None):
        self.model.draw(self.position, shader)

    def destroy(self):
        self.model.destroy()

class ParticleEmitter2DCreateInfo:
    def __init__(self):
        self.pos = None
        self.color = None
        self.lifetime = None
        self.velocity_field = None
        self.size = None
        self.layer = None
        self.shader = None
        self.rate = None
        self.offsetFunction = None

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
        self.offsetFunction = createInfo.offsetFunction
        self.particles = []
        self.t = 0
    
    def update(self):
        #create new particles
        self.t += self.rate
        while (self.t > 1):
            self.t -= 1
            createInfo = view.Particle2DCreateInfo()
            createInfo.size = self.size
            createInfo.color = self.color
            createInfo.layer = self.layer
            offset = self.offsetFunction()
            createInfo.pos = [self.pos[0] + offset[0], self.pos[1] + offset[1]]
            createInfo.shader = self.shader
            createInfo.velocity_field = self.velocity_field
            createInfo.lifetime = self.lifetime
            self.particles.append(view.Particle2D(createInfo))
        
        #update existing particles
        for particle in self.particles:
            particle.update()
        
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

class SmokeCloud:
    pass

class SmokeSource:
    pass
