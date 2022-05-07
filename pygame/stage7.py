"""
    3D Game
"""
################ 3D Game ######################################################
import pygame
import numpy as np
import pyrr
################ Configuration ################################################
pygame.init()

BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
PURPLE = (128,0,255)
WHITE = (255,255,255)

SCREEN_WIDTH = 450
SCREEN_HEIGHT = 300
CENTER = np.array([SCREEN_WIDTH//2,SCREEN_HEIGHT//2])
SCREEN = pygame.display.set_mode((SCREEN_WIDTH*2 + 30,SCREEN_HEIGHT + 100))
CLOCK = pygame.time.Clock()

VIEW_SURFACE = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
VIEW_RECT = pygame.Rect(10,50,SCREEN_WIDTH,SCREEN_HEIGHT)

PROJECTION_SURFACE = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
PROJECTION_RECT = pygame.Rect(SCREEN_WIDTH + 20,50,SCREEN_WIDTH,SCREEN_HEIGHT)

font_name = pygame.font.match_font('arial')
################ Helper Functions #############################################

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def round(array):
    """
        Takes a numpy array and converts it to an array of integers.
    """
    return array.astype(int)

def rotate_point(point,angle):
    point = np.append(point,np.array([0],dtype=np.float32))
    matrix = pyrr.matrix33.create_from_z_rotation(theta=np.radians(angle),dtype=np.float32)
    point = pyrr.matrix33.multiply(point,matrix)
    point = np.delete(point,2)
    return point

def clip_line(a,b):
    """
        take two sets of points representing two line segments,
        calculate the point of intersection between them
    """
    #((x1,y1),(x2,y2)) = a
    #((x3,y3),(x4,y4)) = b

    x1 = a[0][0]
    y1 = a[0][1]
    x2 = a[1][0]
    y2 = a[1][1]

    x3 = b[0][0]
    y3 = b[0][1]
    x4 = b[1][0]
    y4 = b[1][1]

    num_a = (x1*y2 - y1*x2)
    num_b = (x3*y4 - y3*x4)
    den = (x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4)
    x = (num_a*(x3 - x4) - (x1 - x2)*num_b)/den
    y = (num_a*(y3 - y4) - (y1 - y2)*num_b)/den
    return np.array([x,y],dtype=np.float32)

def lines_intersect(movement_line,wall_line):
    """ Returns whether two points cross through a wall """
    #((x1,y1),(x2,y2)) = m
    #((x3,y3),(x4,y4)) = w
    
    x1 = movement_line[0][0]
    y1 = movement_line[0][1]
    x2 = movement_line[1][0]
    y2 = movement_line[1][1]

    x3 = wall_line[0][0]
    y3 = wall_line[0][1]
    x4 = wall_line[1][0]
    y4 = wall_line[1][1]

    if x3==x4:
        #vertical wall
        bottom = max(y3,y4)
        top = min(y3,y4)
        if (y1>bottom and y2>bottom)or(y1<top and y2<top):
            #movement is either completely above or below wall
            return False
        else:
            x = x3
            if (x1-x)*(x2-x)<0:
                #movement goes from right to left of wall (or visa versa)
                return True
            else:
                return False
    else:
        #horizontal wall
        left = min(x3,x4)
        right = max(x3,x4)
        if (x1>right and x2>right)or(x1<left and x2<left):
            #movement is either completely to the left or right of wall
            return False
        else:
            y = y3
            if (y1-y)*(y2-y)<0:
                #movement goes from above to below wall (or visa versa)
                return True
            else:
                return False

def scale(point,factor_x,factor_y=None):
    if factor_y==None:
        factor_y = factor_x
    point = np.append(point,np.array([0],dtype=np.float32))
    matrix = pyrr.matrix33.create_from_scale(scale=np.array([factor_x,factor_y,1],dtype=np.float32),dtype=np.float32)
    point = pyrr.matrix33.multiply(point,matrix)
    point = np.delete(point,2)
    return point

def dot_product(u,v):
    return np.dot(u,v)

def importData(filename):
    with open(filename,'r') as f:
        line = f.readline()
        while line:
            if line[0]=='w':
                #wall
                # w(a_x,a_y,b_x,b_y)
                start = line.find('(')+1
                end = line.find(')')
                line = line[start:end].replace('\n','').split(',')
                l = [float(item) for item in line]
                pos_a = np.array([32*l[0],32*(50-l[1])],dtype=np.float32)
                pos_b = np.array([32*l[2],32*(50-l[3])],dtype=np.float32)
                w = Wall(pos_a,pos_b)
                WALLS.append(w)
            elif line[0]=='p':
                #player
                # p(x,y,direction)
                start = line.find('(')+1
                end = line.find(')')
                line = line[start:end].replace('\n','').split(',')
                l = [float(item) for item in line]
                pos = np.array([32*l[0],32*(50-l[1])],dtype=np.float32)
                player = Player(pos,l[2])
            line = f.readline()
        return player

################ Classes ######################################################

class Player:
    def __init__(self,position,direction):
        self.radius = 16
        self.position = position
        self.direction = direction
        self.speed = 2
        self.camera_z = 30
        self.near_plane = [[-32,0],[32,0]]
        self.near_plane = np.array(self.near_plane,dtype=np.float32)
        self.energy = 0
        
        self.original_image = pygame.Surface((32,32))
        pygame.draw.circle(self.original_image,RED,(16,16),self.radius)
        pygame.draw.line(self.original_image,BLACK,(16,16),(32,16))
    
    def update(self):
        #take inputs
        keystate = pygame.key.get_pressed()

        if keystate[pygame.K_LEFT]:
            self.direction += 2
            if self.direction > 360:
                self.direction -= 360

        if keystate[pygame.K_RIGHT]:
            self.direction -= 2
            if self.direction < 0:
                self.direction += 360

        if keystate[pygame.K_UP]:
            dx =  self.speed*np.cos(np.radians(self.direction))
            dy = -self.speed*np.sin(np.radians(self.direction))
            self.move(dx,dy)

        if keystate[pygame.K_DOWN]:
            dx = -self.speed*np.cos(np.radians(self.direction))
            dy =  self.speed*np.sin(np.radians(self.direction))
            self.move(dx,dy)

        if keystate[pygame.K_SPACE] and self.camera_z==30:
            self.energy = 20
        
        self.camera_z += self.energy
        self.energy -= 1
        if self.camera_z <= 30:
            self.energy = 0
            self.camera_z = 30

        #apply transformations
        self.world_to_view_transform()
    
    def move(self,dx,dy):
        #check movement in x and y direction separately
        temp = np.array([0,0],dtype=np.float32)

        check = np.array([self.radius*dx,0],dtype=np.float32)
        could_move_to = self.position + check
        can_move = True
        for w in WALLS:
            if lines_intersect((self.position,could_move_to),w.getLine()):
                can_move = False
                break
        if can_move:
            temp[0] = dx

        check = np.array([0,self.radius*dy],dtype=np.float32)
        could_move_to = self.position + check
        can_move = True
        for w in WALLS:
            if lines_intersect((self.position,could_move_to),w.getLine()):
                can_move = False
                break
        if can_move:
            temp[1] = dy

        self.position += temp

    def world_to_view_transform(self):
        #apply world to view coordinate transformation
        #rotate then transate
        rotated_image = pygame.transform.rotate(self.original_image, 90)
        rotated_rect = rotated_image.get_rect()
        rotated_rect.center = CENTER
        #blit to view
        VIEW_SURFACE.blit(rotated_image,rotated_rect)
        #draw the near plane
        pygame.draw.line(VIEW_SURFACE,WHITE,round(self.near_plane[0] + CENTER),round(self.near_plane[1] + CENTER))

class Wall:
    def __init__(self,pos_a,pos_b):
        self.pos_a = pos_a
        self.pos_b = pos_b
        self.colour = GREEN
        self.z = 0
        self.height = 80

        #calculate normal
        dx = self.pos_b[0]-self.pos_a[0]
        dy = self.pos_b[1]-self.pos_a[1]
        if dx==0:
            #vertical wall
            self.normal = np.array([dy/abs(dy),0],dtype=np.float32)
        else:
            #horizontal wall
            self.normal = np.array([0,-dx/abs(dx)],dtype=np.float32)
    
    def update(self):
        #backface test
        dir_to_cam = player.position - self.pos_a
        
        if dot_product(dir_to_cam,self.normal)>0:
            self.world_to_view_transform()
            self.view_to_projection_transform()

    def world_to_view_transform(self):
        #find position relative to camera
        self.pos_a_view = self.pos_a - player.position
        self.pos_b_view = self.pos_b - player.position
        #rotate 90 degrees counter clockwise, then opposite camera motion
        opposite_cam = 90-player.direction
        self.pos_a_view = rotate_point(self.pos_a_view,opposite_cam)
        self.pos_b_view = rotate_point(self.pos_b_view,opposite_cam)
        #get normal line to graph
        norm_start = CENTER + (self.pos_a_view+self.pos_b_view)/2
        norm_components = rotate_point(self.normal/10,opposite_cam)
        norm_end = norm_start+norm_components

        pygame.draw.line(VIEW_SURFACE,self.colour,
                            round(self.pos_a_view+CENTER),
                            round(self.pos_b_view+CENTER))
        pygame.draw.line(VIEW_SURFACE,self.colour,round(norm_start),round(norm_end))
    
    def view_to_projection_transform(self):
        #Projection transformation
        #fetch the top-down coordinates
        #(x_a,depth_a) = self.pos_a_view
        #(x_b,depth_b) = self.pos_b_view

        if self.pos_a_view[1] >= 0 and self.pos_b_view[1] >= 0:
            return

        if self.pos_a_view[1] >= 0:
            (x_a,depth_a) = clip_line(
                                        (self.pos_a_view,self.pos_b_view),
                                        player.near_plane
                                    )
        
        if self.pos_b_view[1] >= 0:
            (x_b,depth_b) = clip_line(
                                        (self.pos_a_view,self.pos_b_view),
                                        player.near_plane
                                    )

        self.pos_a_view[1] *= -1
        self.pos_a_view[1] = max(self.pos_a_view[1],0.01)
        x_a = self.pos_a_view[0]/self.pos_a_view[1]
        top_a = -(self.z+self.height-player.camera_z)/self.pos_a_view[1]
        bottom_a = -(self.z-player.camera_z)/self.pos_a_view[1]

        self.pos_b_view[1] *= -1
        self.pos_b_view[1] = max(self.pos_b_view[1],0.01)
        x_b = self.pos_b_view[0]/self.pos_b_view[1]
        top_b = -(self.z+self.height-player.camera_z)/self.pos_b_view[1]
        bottom_b = -(self.z-player.camera_z)/self.pos_b_view[1]

        points = [
                    np.array([x_a,top_a],dtype=np.float32),
                    np.array([x_b,top_b],dtype=np.float32),
                    np.array([x_b,bottom_b],dtype=np.float32),
                    np.array([x_a,bottom_a],dtype=np.float32)
                ]
        
        for i in range(len(points)):
            points[i] = scale(points[i],SCREEN_WIDTH//2,SCREEN_HEIGHT//2)
            points[i] = round(points[i]+CENTER)

        pygame.draw.polygon(PROJECTION_SURFACE, self.colour, points,1)

    def getLine(self):
        return (self.pos_a,self.pos_b)

################ Game Objects #################################################
WALLS = []
player = importData('level.txt')
################ Game Loop ####################################################
running = True
while running:
    ################ Reset Surfaces ###########################################
    VIEW_SURFACE.fill(BLACK)
    PROJECTION_SURFACE.fill(BLACK)
    SCREEN.fill(BLACK)
    ################ Handle Events ############################################
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running = False
    ################ Update ###################################################
    for wall in WALLS:
        wall.update()
    player.update()
    ################ Render ###################################################
    SCREEN.blit(VIEW_SURFACE,VIEW_RECT)
    SCREEN.blit(PROJECTION_SURFACE,PROJECTION_RECT)

    pygame.draw.rect(SCREEN,WHITE,VIEW_RECT,1)
    draw_text(SCREEN,"View Coordinates",16,60,20)
    pygame.draw.rect(SCREEN,WHITE,PROJECTION_RECT,1)
    draw_text(SCREEN,"Projection Coordinates",16,SCREEN_WIDTH+100,20)
    ################ Clock etc ################################################
    CLOCK.tick()
    fps = CLOCK.get_fps()
    pygame.display.set_caption("Running at "+str(int(fps))+" fps")
    pygame.display.update()

################ Shutdown #####################################################
pygame.quit()