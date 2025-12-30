"""
    3D Game
"""
################ 3D Game ######################################################

import pygame
import numpy as np
import math
from numba import jit

################ Helper Functions #############################################

@jit
def round(point):
    return (int(point[0]),int(point[1]))

def translate(point,translation):
    (x,y) = point
    (dx,dy) = translation
    return (x + dx,y + dy)

@jit
def rotate_point(point,angle):
    (x,y) = point
    theta = math.radians(angle)
    rotated_x = x*math.cos(theta) + y*math.sin(theta)
    rotated_y = -x*math.sin(theta) + y*math.cos(theta)
    return (rotated_x,rotated_y)

@jit
def clip_line(line_a,line_b):
    ((x1,y1),(x2,y2)) = line_a
    ((x3,y3),(x4,y4)) = line_b

    num_a = (x1*y2 - y1*x2)
    num_b = (x3*y4 - y3*x4)
    den = (x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4)
    x = (num_a*(x3 - x4) - (x1 - x2)*num_b)/den
    y = (num_a*(y3 - y4) - (y1 - y2)*num_b)/den
    return (x,y)

@jit
def scale(point,factor_x,factor_y=None):
    if factor_y==None:
        factor_y = factor_x
    (x,y) = point
    return (x*factor_x,y*factor_y)

@jit
def dot_product(u,v):
    (u1,u2) = u
    (v1,v2) = v
    return u1*v1 + u2*v2

@jit
def quick_distance(pos_a,pos_b):
    dx = abs(pos_a[0] - pos_b[0])
    dy = abs(pos_a[1] - pos_b[1])
    return dx + dy
    
################ Classes ######################################################

class Player:

    def __init__(self,x,y,direction,room):
        self.radius = 12
        self.position = (x,y)
        self.direction = direction
        self.speed = 2
        self.camera_z = 30
        self.near_plane = ((-32,0),(32,0))
        self.energy = 0
        self.sector = None

    def setRoom(self,newRoom):
        self.room = newRoom
        self.recalculateSector()

    def recalculateSector(self):
        for s in self.room.getSectors():
            if s.inSector(self.position):
                self.sector = s
                break

    def update(self, dt):

        self.camera_z += self.energy*dt
        self.energy -= 1*dt
        if self.camera_z <= 30:
            self.energy = 0
            self.camera_z = 30

    def move(self,dx,dy):
        #check movement in x and y direction separately
        temp = [0,0]

        check = (dx,0)
        could_move_to = translate(self.position,check)
        if not self.sector.hitWall(could_move_to,self.radius,check):
            temp[0] = dx

        check = (0,dy)
        could_move_to = translate(self.position,check)
        if not self.sector.hitWall(could_move_to,self.radius,check):
            temp[1] = dy

        self.position = translate(self.position,temp)
        self.sector = self.sector.newSector(self.position)
        if self.sector is None:
            #may have crossed a door!
            #select nearest door
            for d in self.room.doors:
                if quick_distance(self.position,d.mid)<=32:
                    break
            self.setRoom(d.getRoom(self.position))

class Wall:


    def __init__(self,pos_a,pos_b):

        self.pos_a = pos_a
        self.pos_b = pos_b
        self.z = 0
        self.height = 80
        self.tag = "wall"

        #calculate normal
        dx = self.pos_b[0]-self.pos_a[0]
        dy = self.pos_b[1]-self.pos_a[1]
        if dx==0:
            #vertical wall
            self.normal = (dy/abs(dy),0)
        else:
            #horizontal wall
            self.normal = (0,-dx/abs(dx))

    def getLine(self):
        return (self.pos_a,self.pos_b)

class Door(Wall):


    def __init__(self,pos_a,pos_b,room_lu,room_rd):

        super().__init__(pos_a,pos_b)
        self.room_lu = room_lu
        self.room_lu.addDoor(self)
        self.room_rd = room_rd
        self.room_rd.addDoor(self)
        self.is_open = False
        self.mid = scale(translate(self.pos_a,self.pos_b),0.5)

    def getRoom(self,pos):
        if self.normal[0]==0:
            #horizontal door
            if pos[1] < self.pos_a[1]:
                return self.room_lu
            else:
                return self.room_rd
        else:
            #vertical door
            if pos[0] < self.pos_a[0]:
                return self.room_lu
            else:
                return self.room_rd

    def open(self):

        self.room_lu.activate()
        self.room_rd.activate()
        self.is_open = True

    def close(self, player_position):

        self.is_open = False
        pos = player_position
        if self.normal[0]==0:
            #horizontal door
            if pos[1] < self.pos_a[1]:
                self.room_rd.deactivate()
            else:
                self.room_lu.deactivate()
        else:
            #vertical door
            if pos[0] < self.pos_a[0]:
                self.room_rd.deactivate()
            else:
                self.room_lu.deactivate()

    def update(self, player_position):

        if quick_distance(self.mid,player_position) <= 32:
            if not self.is_open:
                self.open()
        elif self.is_open:
            self.close(player_position)

class Sector:


    def __init__(self,pos,size,sides):

        self.position = pos
        self.size = size
        self.sides = sides
        self.tag = ""

        self.pos_a = self.position
        self.pos_b = (self.position[0],self.position[1]+self.size[1])
        self.pos_c = (self.position[0]+self.size[0],self.position[1]+self.size[1])
        self.pos_d = (self.position[0]+self.size[0],self.position[1])

        #meta-data
        self.walls = []
        self.connects_ab = None
        self.connects_bc = None
        self.connects_cd = None
        self.connects_da = None
        #construct walls
        if sides[0]:
            #north
            self.walls.append(Wall(self.pos_d,self.pos_a))
        if sides[1]:
            #east
            self.walls.append(Wall(self.pos_c,self.pos_d))
        if sides[2]:
            #south
            self.walls.append(Wall(self.pos_b,self.pos_c))
        if sides[3]:
            #west
            self.walls.append(Wall(self.pos_a,self.pos_b))

    def getCorners(self):
        return (
                    self.pos_a,
                    self.pos_b,
                    self.pos_c,
                    self.pos_d
                )

    def inSector(self,pos):
        if pos[0] < self.pos_a[0]:
            return False
        if pos[0] > self.pos_c[0]:
            return False
        if pos[1] < self.pos_a[1]:
            return False
        if pos[1] > self.pos_c[1]:
            return False
        return True
    
    def newSector(self,pos):
        #west
        if pos[0] < self.pos_a[0]:
            return self.connects_ab
        #east
        if pos[0] > self.pos_c[0]:
            return self.connects_cd
        #north
        if pos[1] < self.pos_a[1]:
            return self.connects_da
        #south
        if pos[1] > self.pos_c[1]:
            return self.connects_bc
        return self
    
    def hitWall(self,pos,size,velocity):
        (vx,vy) = velocity
        if vx<0:
            #west
            west = pos[0] - size
            if west < self.pos_a[0] and self.sides[3]:
                return True
        elif vx>0:
            #east
            east = pos[0] + size
            if east > self.pos_c[0] and self.sides[1]:
                return True
        
        if vy<0:
            #north
            north = pos[1] - size
            if north < self.pos_a[1] and self.sides[0]:
                return True
        elif vy>0:
            #south
            south = pos[1] + size
            if south > self.pos_c[1] and self.sides[2]:
                return True
        return False

class Room:

    def __init__(self):
        self.sectors = []
        self.tag = ""
        self.doors = []
        self.active = False

    def addSector(self,sector):
        if sector not in self.sectors:
            self.sectors.append(sector)

    def addDoor(self,door):
        if door not in self.doors:
            self.doors.append(door)

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def getSectors(self):
        return self.sectors

    def update(self, player_position):
        for d in self.doors:
            d.update(player_position)

class Scene:

    def __init__(self):
        self.ROOMS = []
        self.ACTIVE_ROOMS = []
        self.SECTORS = []
        self.player = None
        self.importData('level3.txt')
        self.connect_sectors()
    
    def importData(self, filename):
        #read file
        with open(filename,'r') as f:
            line = f.readline()
            while line:
                start = line.find('(')+1
                end = line.find(')')
                tag = line[0:start-1]
                line_split = line[start:end].replace('\n','').split(',')
                if line[0]=='r':
                    self.add_room(tag)
                elif line[0]=='s':
                    self.add_sector(line_split, tag)
                elif line[0]=='d':
                    self.add_door(line_split, tag)
                elif line[0]=='p':
                    self.add_player(line_split)
                line = f.readline()
    
    def add_room(self, tag):

        r = Room()
        r.tag = tag
        self.ROOMS.append(r)

    def add_sector(self, line, tag):

        #sector
        # s(x,y,width,height,n,e,s,w,room)
        pos = (32*float(line[0]),32*(50-float(line[1])))
        size = (32*float(line[2]),32*float(line[3]))
        sides = (int(line[4]),int(line[5]),int(line[6]),int(line[7]))
        s = Sector(pos,size,sides)
        self.find_room(line[8]).addSector(s)
        s.tag = tag
        self.SECTORS.append(s)
    
    def add_door(self, line, tag):

        #door
        # s(x_a,y_a,x_b,y_b,room_lu,room_rd)
        pos_a = (32*float(line[0]),32*(50-float(line[1])))
        pos_b = (32*float(line[2]),32*(50-float(line[3])))
        room_lu = self.find_room(line[4])
        room_rd = self.find_room(line[5])
        d = Door(pos_a,pos_b,room_lu,room_rd)
        d.tag = tag
    
    def add_player(self, line):

        #player
        # p(x,y,direction,room)
        self.player = Player(32*float(line[0]),32*(50-float(line[1])),float(line[2]),line[3])
        self.player.room = self.find_room(line[3])
        self.player.room.activate()
        self.player.recalculateSector()
        
    def find_room(self, tag):
        for r in self.ROOMS:
            if r.tag == tag:
                return r
        return None

    def connect_sectors(self):

        for r in self.ROOMS:
            for obj in r.getSectors():
                A = obj.pos_a
                B = obj.pos_b
                C = obj.pos_c
                D = obj.pos_d
                for obj2 in r.getSectors():
                    hasA = False
                    hasB = False
                    hasC = False
                    hasD = False
                    if obj==obj2:
                        continue
                    corners = obj2.getCorners()
                    #do any corners match?
                    for corner in corners:
                        if A[0] == corner[0] and A[1] == corner[1]:
                            hasA = True
                            continue
                        elif B[0] == corner[0] and B[1] == corner[1]:
                            hasB = True
                            continue
                        elif C[0] == corner[0] and C[1] == corner[1]:
                            hasC = True
                            continue
                        elif D[0] == corner[0] and D[1] == corner[1]:
                            hasD = True
                            continue
                    if hasA and hasB:
                        obj.connects_ab = obj2
                        #print(f"{obj.tag} connects to {obj2.tag}")
                        continue
                    elif hasB and hasC:
                        obj.connects_bc = obj2
                        #print(f"{obj.tag} connects to {obj2.tag}")
                        continue
                    elif hasC and hasD:
                        obj.connects_cd = obj2
                        #print(f"{obj.tag} connects to {obj2.tag}")
                        continue
                    elif hasD and hasA:
                        obj.connects_da = obj2
                        #print(f"{obj.tag} connects to {obj2.tag}")
                        continue

    def update(self, dt):

        for r in self.ACTIVE_ROOMS:
            r.update(self.player.position)
        self.player.update(dt)

        self.ACTIVE_ROOMS = []
        for r in self.ROOMS:
            if r.active:
                self.ACTIVE_ROOMS.append(r)

    def spin_player(self, dTheta):

        self.player.direction += dTheta
        
        if self.player.direction > 360:
            self.player.direction -= 360
        elif self.player.direction < 0:
            self.player.direction += 360

    def move_player(self, dt):

        dx =  self.player.speed*math.cos(math.radians(self.player.direction))*dt
        dy = -self.player.speed*math.sin(math.radians(self.player.direction))*dt
        self.player.move(dx, dy)
    
    def strafe_player(self, dt):

        dx =  self.player.speed*math.cos(math.radians(self.player.direction + 90))*dt
        dy = -self.player.speed*math.sin(math.radians(self.player.direction + 90))*dt
        self.player.move(dx, dy)

    def throw_player(self, energy):

        if self.player.camera_z==30:
            self.player.energy = energy

class Engine:

    def __init__(self, width, height):

        self.BLACK = (0,0,0)
        self.RED = (255,0,0)
        self.GREEN = (0,255,0)
        self.BLUE = (0,0,255)
        self.YELLOW = (255,255,0)
        self.PURPLE = (128,0,255)
        self.CYAN = (0,255,255)
        self.WHITE = (255,255,255)

        self.SCREEN_WIDTH = width
        self.SCREEN_HEIGHT = height

        self.SCREEN = pygame.display.set_mode((self.SCREEN_WIDTH,self.SCREEN_HEIGHT))
        self.font_name = pygame.font.match_font('arial')
    
    def render(self, scene):

        self.SCREEN.fill(self.BLACK)

        for r in scene.ACTIVE_ROOMS:

            for s in r.sectors:
                for w in s.walls:
                    self.draw_wall(w, scene.player, False, self.GREEN)
            for d in r.doors:

                if d.is_open:
                    color = self.YELLOW
                else:
                    color = self.CYAN
                self.draw_wall(d, scene.player, True, color)

    def draw_text(self, surf, text, size, x, y):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect()
        text_rect.bottomleft = (x, y)
        surf.blit(text_surface, text_rect)

    def draw_wall(self, wall, player, both_faces, color):

        #backface test
        dx = player.position[0] - wall.pos_a[0]
        dy = player.position[1] - wall.pos_a[1]
        dir_to_cam = (dx,dy)

        if not both_faces and dot_product(dir_to_cam, wall.normal)<=0:
            return None
            
        #find position relative to camera
        cam = (-player.position[0],-player.position[1])
        pos_a_view = translate(wall.pos_a, cam)
        pos_b_view = translate(wall.pos_b,cam)
        #rotate 90 degrees counter clockwise, then opposite camera motion
        opposite_cam = 90-player.direction
        pos_a_view = rotate_point(pos_a_view,opposite_cam)
        pos_b_view = rotate_point(pos_b_view,opposite_cam)

        #Projection transformation
        #fetch the top-down coordinates
        (x_a,depth_a) = pos_a_view
        (x_b,depth_b) = pos_b_view

        if depth_a >= 0 and depth_b >= 0:
            return None

        if depth_a >= 0:
            (x_a,depth_a) = clip_line(
                                    ((x_a,depth_a),(x_b,depth_b)),
                                    player.near_plane
                                )

        if depth_b >= 0:
            (x_b,depth_b) = clip_line(
                                    ((x_a,depth_a),(x_b,depth_b)),
                                    player.near_plane
                                )

        depth_a *= -1
        depth_a = max(depth_a,0.01)
        x_a = pos_a_view[0]/depth_a
        top_a = -(wall.z+wall.height-player.camera_z)/depth_a
        bottom_a = -(wall.z-player.camera_z)/depth_a

        depth_b *= -1
        depth_b = max(depth_b,0.01)
        x_b = pos_b_view[0]/depth_b
        top_b = -(wall.z+wall.height-player.camera_z)/depth_b
        bottom_b = -(wall.z-player.camera_z)/depth_b

        points = [
                    (x_a,top_a),
                    (x_b,top_b),
                    (x_b,bottom_b),
                    (x_a,bottom_a)
                ]
        
        for i in range(len(points)):
            points[i] = scale(points[i],self.SCREEN_WIDTH//2,self.SCREEN_HEIGHT//2)
            points[i] = round(translate(points[i],(320,240)))

        pygame.draw.polygon(self.SCREEN, color, points,1)

class App:

    def __init__(self, width, height):

        pygame.init()
        self.CLOCK = pygame.time.Clock()
        pygame.mouse.set_pos((320,240))
        pygame.mouse.set_visible(False)

        self.level = Scene()
        self.engine = Engine(width, height)
        self.dt = 0
    
    def handle_keys(self):

        keystate = pygame.key.get_pressed()

        if keystate[pygame.K_LEFT]:
            self.level.spin_player(2 * self.dt)

        if keystate[pygame.K_RIGHT]:
            self.level.spin_player(-2 * self.dt)

        if keystate[pygame.K_UP] or keystate[pygame.K_w]:
            
            self.level.move_player(self.dt)

        if keystate[pygame.K_DOWN] or keystate[pygame.K_s]:

            self.level.move_player(-self.dt)
        
        if keystate[pygame.K_a]:
            
            self.level.strafe_player(self.dt)

        if keystate[pygame.K_d]:

            self.level.strafe_player(-self.dt)

        if keystate[pygame.K_SPACE]:
            self.level.throw_player(20)

    def handle_mouse(self):

        (x,y) = pygame.mouse.get_pos()
        theta_increment = self.dt * 0.5 * (320 - x)
        self.level.spin_player(theta_increment)
        pygame.mouse.set_pos((320,240))

    def run(self):

        running = True
        while running:
            self.CLOCK.tick()
            
            ################ Handle Events ############################################
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
            self.handle_keys()
            self.handle_mouse()
            ################ Update ###################################################
            self.level.update(self.dt)
            ################ Render ###################################################
            self.engine.render(self.level)
            ################ Clock etc ################################################
            self.dt = self.CLOCK.get_time()/17
            self.CLOCK.tick(60)
            fps = self.CLOCK.get_fps()
            pygame.display.set_caption("Running at "+str(int(fps))+" fps")
            pygame.display.update()

################ Shutdown #####################################################

game = App(640, 480)
game.run()
pygame.quit()