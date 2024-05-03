from config import *
BG_GRID_SIZE = 128
RADIUS = 64
RIGIDITY = 0.4
SPRING_CONSTANT = 0.5

class World:


    def __init__(self, resolution: int):

        self.last_velocity_x = 0.0
        self.last_velocity_y = 0.0

        #build background
        self.bg = []
        for x in range(0,SCREEN_WIDTH, BG_GRID_SIZE):
            for y in range(0, SCREEN_HEIGHT, BG_GRID_SIZE):
                self.bg.append([x,y])
        
        #control points
        self.control_points = [
            [SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2],
            [SCREEN_WIDTH / 2 + RADIUS, SCREEN_HEIGHT / 2]]
        self.angular_velocity = 0
        self.linear_velocity = 0

        #nodes
        self.original_points = []
        self.image = []
        for i in range(resolution):
            t = i / (resolution - 1)
            theta = (1.0 - t) * -np.pi/2 + t * np.pi/2
            c = np.cos(theta)
            s = np.sin(theta)
            if theta > 0:
                x = self.control_points[0][0] + 2 * RADIUS * c ** 3
            else:
                x = self.control_points[0][0] + 2 * RADIUS * c
            y = self.control_points[0][1] - 2 * RADIUS * s
            self.original_points.append([x, y])
            self.image.append([x, y])
    
    def update(self, frame_time: float, velocity_x: float, velocity_y: float):

        rate = frame_time / 16.7
        impulse = np.array((velocity_x - self.last_velocity_x, 
                            velocity_y - self.last_velocity_y, 0.0),
                            dtype = np.float32)
        self.last_velocity_x = velocity_x
        self.last_velocity_y = velocity_y

        for particle in self.bg:
            particle[0] -= velocity_x * rate
            if particle[0] < 0:
                particle[0] += SCREEN_WIDTH
            if particle[0] > SCREEN_WIDTH:
                particle[0] -= SCREEN_WIDTH
            
            particle[1] -= velocity_y * rate
            if particle[1] < 0:
                particle[1] += SCREEN_HEIGHT
            if particle[1] > SCREEN_HEIGHT:
                particle[1] -= SCREEN_HEIGHT

        #read data
        dx = self.control_points[1][0] - self.control_points[0][0]
        dy = self.control_points[0][1] - self.control_points[1][1]
        theta = np.degrees(np.arctan(dy/dx))
        axis = np.array((dx,dy,0.0), dtype=np.float32)
        radius = np.linalg.norm(axis)
        axis /= radius
        net_force_tangent = 0.0
        net_force_axis = 0.0

        #gravity
        gravity = np.array((0,-1,0), dtype=np.float32)
        net_force_tangent -= np.cross(gravity, axis)[2]
        net_force_axis += abs(np.dot(gravity, axis))

        #impulse
        net_force_tangent += np.cross(impulse, axis)[2]
        net_force_axis -= np.dot(impulse, axis)

        #elasticity
        stretch = RADIUS - radius
        net_force_axis += SPRING_CONSTANT * stretch

        #friction
        self.linear_velocity *= 0.99

        self.angular_velocity += rate * net_force_tangent
        if abs(self.angular_velocity) < 0.001:
            self.angular_velocity = 0.0
        theta += rate * self.angular_velocity

        self.linear_velocity += rate * net_force_axis
        if abs(self.linear_velocity) < 0.001:
            self.linear_velocity = 0.0
        radius += rate * self.linear_velocity
        
        #boundary conditions
        if theta < -75:
            #rebound
            theta -= rate * self.angular_velocity
            self.angular_velocity *= -(1 - RIGIDITY)
            theta += rate * self.angular_velocity
        if theta > 75:
            theta -= rate * self.angular_velocity
            self.angular_velocity = 0

        #resolve
        t = np.radians(theta)
        c = np.cos(t)
        s = np.sin(t)
        self.control_points[1][0] = self.control_points[0][0] + radius * c
        self.control_points[1][1] = self.control_points[0][1] - radius * s

        alpha = dy
        for i in range(1, len(self.original_points) - 1):
            x = self.original_points[i][0]
            y = self.original_points[i][1]
            dx = (x - 400) / 400
            self.image[i][0] = x
            self.image[i][1] = y - 4 * alpha * dx
    
    def get_bg(self) -> list[tuple[float]]:
        return self.bg
    
    def get_control_points(self) -> list[tuple[float]]:
        return self.control_points
    
    def get_image(self) -> list[tuple[float]]:
        return self.image