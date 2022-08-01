from turtle import right
from config import *

class Player:

    def __init__(self, position):

        self.theta = 0
        self.position = np.array(position,dtype=np.float32)
        self.velocity = np.array([0,0,0], dtype=np.float32)
        self.acceleration = np.array([0,0,-0.5], dtype=np.float32)
        self.terminal_velocity = 0
        self.fall_velocity = -3
        self.float_velocity = -0.5
        self.jumping = False
        self.jump_count = 0
        self.spacebar_down = False
        self.float_t = 0
        self.float_t_max = 5_000
        self.floating = False
        self.modelTransform = pyrr.matrix44.create_from_translation(vec = self.position, dtype = np.float32)
        self.color = np.array([0,0,1], dtype=np.float32)

    def move(self, direction, amount):

        if self.floating:
            direction = 0
            amount *= 0.5

        walkDirection = (direction + self.theta) % 360
        movement = amount * np.array(
            [
                np.cos(np.radians(walkDirection),dtype=np.float32), 
                np.sin(np.radians(walkDirection),dtype=np.float32), 
                0
            ], dtype = np.float32)
        self.position += movement

        self.modelTransform = pyrr.matrix44.create_from_translation(vec = self.position, dtype = np.float32)

        return movement
    
    def apply_impulse(self, impulse):

        self.velocity += impulse
    
    def try_jump(self, direction, amount):

        if self.jumping and self.jump_count >= 3:
            return

        self.jumping = True
        self.jump_count += 1
        self.float_t = 0
        impulse = np.array(
            [
                amount * np.cos(np.radians(direction + self.theta),dtype=np.float32), 
                amount * np.sin(np.radians(direction + self.theta),dtype=np.float32), 
                8
            ], dtype = np.float32)
        self.apply_impulse(impulse)
    
    def calculate_jump(self, dt):

        old_position = np.copy(self.position)

        self.velocity += dt * self.acceleration

        can_float = (self.velocity[2] < self.float_velocity) \
                    and (self.spacebar_down) and (self.jumping) \
                    and (self.float_t < self.float_t_max) \
                    and (self.jump_count <= 3)
        
        if can_float:

            self.terminal_velocity = self.float_velocity
            self.float_t += 17.67 * dt
            self.color[1] = 1
        
        else:

            self.terminal_velocity = self.fall_velocity
            self.color[1] = 0
        
        self.velocity[2] = max(self.velocity[2], self.terminal_velocity)

        self.position += dt * self.velocity

        if self.position[2] <= 0.9:

            self.position[2] = 0.9
            self.velocity = 0 * self.velocity
            self.jumping = False
            self.jump_count = 0
        
        self.color[0] = self.jump_count / 3.0

        self.modelTransform = pyrr.matrix44.create_from_translation(vec = self.position, dtype = np.float32)

        return self.position - old_position

class Camera:

    def __init__(self, position):

        self.position = np.array(position,dtype=np.float32)
        self.forward = np.array([0, 0, 0],dtype=np.float32)
        self.right = np.array([0, 0, 0],dtype=np.float32)
        self.up = np.array([0, 0, 0],dtype=np.float32)
        self.global_up = np.array([0, 0, 1], dtype=np.float32)
        self.arm_length = 7

    def update(self, target_position, dt):

        selfToTarget = target_position - self.position
        distance = pyrr.vector.length(selfToTarget)
        if np.abs(distance - self.arm_length) > 0.1:
            forwardAmount = dt * (distance - self.arm_length)
            self.move_forwards(forwardAmount)
        
        self.forward = pyrr.vector.normalize(selfToTarget)
        self.right = pyrr.vector.normalize(pyrr.vector3.cross(self.global_up,self.forward))
        self.up = pyrr.vector.normalize(pyrr.vector3.cross(self.forward,self.right))

        self.viewTransform = pyrr.matrix44.create_look_at(
            eye = self.position, target = target_position, 
            up = self.up, dtype=np.float32
        )
    
    def move(self, velocity):

        self.position += velocity
    
    def strafe(self, right_amount, up_amount):

        self.position += right_amount * self.right + up_amount * self.up
    
    def move_forwards(self, forward_amount):

        self.position += forward_amount * self.forward

class Ground:

    def __init__(self, z):

        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)

        self.z = z

    def update(self, playerPos):

        position = np.array([playerPos[0], playerPos[1], self.z], dtype=np.float32)
        self.modelTransform = pyrr.matrix44.create_from_translation(
            vec = position, dtype = np.float32
        )

class Scene:

    def __init__(self):

        self.create_objects()

    def create_objects(self):
        
        self.player = Player(position = [0,0,0.9])
        self.camera = Camera(position = [-7.2,0,3.6])
        self.ground = Ground(z = 0)

    def update(self, dt):

        self.ground.update(playerPos=self.player.position)
        self.camera.update(target_position=self.player.position, dt=dt)
        movement = self.player.calculate_jump(dt)
        self.camera.move(movement)

    def move_player(self, direction, amount):

        movement = self.player.move(direction, amount)
        self.camera.move(movement)

    def strafe_camera(self, right_amount, up_amount):

        self.camera.strafe(right_amount, up_amount)

        cameraToPlayer = self.player.position - self.camera.position

        newDirection = np.degrees(
            np.arctan2(cameraToPlayer[1], cameraToPlayer[0])
        )

        self.player.theta = newDirection
    
    def set_camera_zoom(self, distance):

        self.camera.arm_length = distance
    
    def set_spacebar_status(self, status):

        self.player.spacebar_down = status
    
    def try_jump(self, direction, amount):

        self.player.try_jump(direction, amount)
