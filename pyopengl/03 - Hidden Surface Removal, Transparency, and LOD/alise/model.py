from config import *
import geometry

class Block:

    def __init__(self, position):

        self.box = geometry.Box3D(8, 8, 1, position)

        self.original_color = np.array([0.5,0.5,0.7], dtype=np.float32)
        self.modelTransform = pyrr.matrix44.create_from_translation(vec = self.box.center, dtype = np.float32)
    
    def reset_color(self):

        self.color = self.original_color

class Player:

    def __init__(self, position):

        self.box = geometry.Box3D(0.7, 0.7, 1.8, position)
        self.old_position = np.copy(self.box.center)
        self.on_ground = True

        self.theta = 0
        self.velocity = np.array([0,0,0], dtype=np.float32)
        self.acceleration = np.array([0,0,-0.125], dtype=np.float32)

        self.terminal_velocity = 0
        self.fall_velocity = -0.5
        self.float_velocity = -0.125
        self.jump_energy = 2

        self.jump_count = 0
        self.spacebar_down = False
        self.float_t = 0
        self.float_t_max = 5_000
        self.floating = False
        self.modelTransform = pyrr.matrix44.create_from_translation(vec = self.box.center, dtype = np.float32)
        self.color = np.array([0,0,1], dtype=np.float32)

    def move(self, direction, amount, float_forwards = False):

        walkDirection = (direction + self.theta) % 360

        if self.floating:
            amount *= 0.25

        if float_forwards:
            self.velocity[0] += amount * np.cos(np.radians(walkDirection),dtype=np.float32)
            self.velocity[1] += amount * np.sin(np.radians(walkDirection),dtype=np.float32)
        
        else:
            self.velocity[0] = amount * np.cos(np.radians(walkDirection),dtype=np.float32)
            self.velocity[1] = amount * np.sin(np.radians(walkDirection),dtype=np.float32)
    
    def apply_impulse(self, impulse):

        self.velocity = impulse
    
    def try_jump(self, direction, amount):

        self.jump_count += 1

        if self.jump_count > 4:
            return

        self.on_ground = False
        self.float_t = 0
        impulse = np.array(
            [
                amount * np.cos(np.radians(direction + self.theta),dtype=np.float32), 
                amount * np.sin(np.radians(direction + self.theta),dtype=np.float32), 
                self.jump_energy
            ], dtype = np.float32)
        self.apply_impulse(impulse)
    
    def calculate_velocity(self, dt):

        self.old_position = np.copy(self.box.center)

        self.velocity += dt * self.acceleration

        can_float = (self.velocity[2] < self.float_velocity) \
                    and (self.spacebar_down) and (not self.on_ground) \
                    and (self.float_t < self.float_t_max) \
                    and (self.jump_count <= 3)
        
        if can_float:

            self.floating = True
            self.move(0, dt, float_forwards=True)
            self.terminal_velocity = self.float_velocity
            self.float_t += 17.67 * dt
        
        else:

            self.floating = False
            self.terminal_velocity = self.fall_velocity
        
        self.velocity[2] = max(self.velocity[2], self.terminal_velocity)
    
    def update(self):

        if self.on_ground:
            self.jump_count = 0

        self.velocity[0] = 0
        self.velocity[1] = 0

        self.modelTransform = pyrr.matrix44.create_from_translation(vec = self.box.center, dtype = np.float32)

class Camera:

    def __init__(self, position):

        self.position = np.array(position,dtype=np.float32)
        self.forward = np.array([0, 0, 0],dtype=np.float32)
        self.right = np.array([0, 0, 0],dtype=np.float32)
        self.up = np.array([0, 0, 0],dtype=np.float32)
        self.global_up = np.array([0, 0, 1], dtype=np.float32)
        self.arm_length = 10

    def update(self, target_position, dt):

        selfToTarget = target_position - self.position
        max_arm_length = geometry.grid.get_length_to_hit(
            np.copy(target_position), 
            -pyrr.vector.normalize(selfToTarget),
            0.8, self.arm_length
        )
        distance = pyrr.vector.length(selfToTarget)
        if np.abs(distance - max_arm_length) > 0.1:
            forwardAmount = dt * (distance - max_arm_length)
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
        geometry.grid.add(self.player)
        self.camera = Camera(position = [-7.2,0,3.6])
        self.ground = Ground(z = 0)
        self.blocks = []
        for x in range(-128, 128, 16):
            for y in range(-128, 128, 16):
                for z in range(0, 128, 16):
                    if x == 0  and y == 0 and z == 0:
                        continue
                    if (np.random.uniform(0.0, 1.0) > 0.7):
                        self.blocks.append(Block((
                            x + np.random.uniform(0, 16),
                            y + np.random.uniform(0, 16),
                            z + np.random.uniform(0, 16))))
        for block in self.blocks:
            geometry.grid.add(block)
    
    def get_static_geometry(self) -> list[Block]:

        return self.blocks

    def update(self, dt):

        for block in self.blocks:
            block.reset_color()

        self.ground.update(playerPos=self.player.box.center)

        self.player.calculate_velocity(dt)
        geometry.grid.move(self.player, dt)
        self.player.update()

        self.camera.move(self.player.box.center - self.player.old_position)
        self.camera.update(target_position=self.player.box.center, dt=dt)
    
    def move_player(self, direction, amount):

        self.player.move(direction, amount)

    def strafe_camera(self, right_amount, up_amount):

        self.camera.strafe(right_amount, up_amount)

        cameraToPlayer = self.player.box.center - self.camera.position

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