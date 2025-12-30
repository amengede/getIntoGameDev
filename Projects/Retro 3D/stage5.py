"""
    3D Game
"""
################ 3D Game ######################################################
import pygame
import math
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
CENTER = (SCREEN_WIDTH//2,SCREEN_HEIGHT//2)
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

def round(point):
    return (int(point[0]),int(point[1]))

def translate(point,translation):
    (x,y) = point
    (dx,dy) = translation
    return (x + dx,y + dy)

def rotate_point(point,angle):
    (x,y) = point
    theta = math.radians(angle)
    rotated_x = x*math.cos(theta) + y*math.sin(theta)
    rotated_y = -x*math.sin(theta) + y*math.cos(theta)
    return (rotated_x,rotated_y)

def clip_line(line_a,line_b):
    ((x1,y1),(x2,y2)) = line_a
    ((x3,y3),(x4,y4)) = line_b

    num_a = (x1*y2 - y1*x2)
    num_b = (x3*y4 - y3*x4)
    den = (x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4)
    x = (num_a*(x3 - x4) - (x1 - x2)*num_b)/den
    y = (num_a*(y3 - y4) - (y1 - y2)*num_b)/den
    return (x,y)

def lines_intersect(movement_line,wall_line):
    """ Returns whether two points cross through a wall """
    ((x1,y1),(x2,y2)) = movement_line
    ((x3,y3),(x4,y4)) = wall_line
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
    (x,y) = point
    return (x*factor_x,y*factor_y)

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
                w = Wall((32*l[0],32*(50-l[1])),(32*l[2],32*(50-l[3])))
                WALLS.append(w)
            elif line[0]=='p':
                #player
                # p(x,y,direction)
                start = line.find('(')+1
                end = line.find(')')
                line = line[start:end].replace('\n','').split(',')
                l = [float(item) for item in line]
                player = Player(32*l[0],32*(50-l[1]),l[2])
            line = f.readline()
        return player

################ Classes ######################################################

class Player:
    def __init__(self,x,y,direction):

        self.radius = 16
        self.position = (x,y)
        self.direction = direction
        self.speed = 2
        self.camera_z = 30
        self.near_plane = ((-32,0),(32,0))
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
            dx =  self.speed*math.cos(math.radians(self.direction))
            dy = -self.speed*math.sin(math.radians(self.direction))
            self.move(dx,dy)

        if keystate[pygame.K_DOWN]:
            dx = -self.speed*math.cos(math.radians(self.direction))
            dy =  self.speed*math.sin(math.radians(self.direction))
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
        temp = [0,0]

        check = (self.radius*dx,0)
        could_move_to = translate(self.position,check)
        can_move = True
        for w in WALLS:
            if lines_intersect((self.position,could_move_to),w.getLine()):
                can_move = False
                break
        if can_move:
            temp[0] = dx

        check = (0,self.radius*dy)
        could_move_to = translate(self.position,check)
        can_move = True
        for w in WALLS:
            if lines_intersect((self.position,could_move_to),w.getLine()):
                can_move = False
                break
        if can_move:
            temp[1] = dy

        self.position = translate(self.position,temp)

    def world_to_view_transform(self):
        #apply world to view coordinate transformation
        #rotate then transate
        rotated_image = pygame.transform.rotate(self.original_image, 90)
        rotated_rect = rotated_image.get_rect()
        rotated_rect.center = CENTER
        #blit to view
        VIEW_SURFACE.blit(rotated_image,rotated_rect)
        #draw the near plane
        pygame.draw.line(VIEW_SURFACE,WHITE,translate(self.near_plane[0],CENTER),translate(self.near_plane[1],CENTER))

class Wall:
    def __init__(self,pos_a,pos_b):
        self.pos_a = pos_a
        self.pos_b = pos_b
        self.colour = GREEN
        self.z = 0
        self.height = 80
    
    def update(self):
        #wall is already defined in world coordinates
        self.world_to_view_transform()
        self.view_to_projection_transform()

    def world_to_view_transform(self):
        #find position relative to camera
        cam = (-player.position[0],-player.position[1])
        self.pos_a_view = translate(self.pos_a,cam)
        self.pos_b_view = translate(self.pos_b,cam)
        #rotate 90 degrees counter clockwise, then opposite camera motion
        opposite_cam = 90-player.direction
        self.pos_a_view = rotate_point(self.pos_a_view,opposite_cam)
        self.pos_b_view = rotate_point(self.pos_b_view,opposite_cam)

        pygame.draw.line(VIEW_SURFACE,self.colour,
                            round(translate(self.pos_a_view,CENTER)),
                            round(translate(self.pos_b_view,CENTER)))
    
    def view_to_projection_transform(self):
        #Projection transformation
        #fetch the top-down coordinates
        (x_a,depth_a) = self.pos_a_view
        (x_b,depth_b) = self.pos_b_view

        if depth_a >= 0 and depth_b >= 0:
            return

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
        x_a = self.pos_a_view[0]/depth_a
        top_a = -(self.z+self.height-player.camera_z)/depth_a
        bottom_a = -(self.z-player.camera_z)/depth_a

        depth_b *= -1
        depth_b = max(depth_b,0.01)
        x_b = self.pos_b_view[0]/depth_b
        top_b = -(self.z+self.height-player.camera_z)/depth_b
        bottom_b = -(self.z-player.camera_z)/depth_b

        points = [
                    (x_a,top_a),
                    (x_b,top_b),
                    (x_b,bottom_b),
                    (x_a,bottom_a)
                ]
        
        for i in range(len(points)):
            points[i] = scale(points[i],SCREEN_WIDTH//2,SCREEN_HEIGHT//2)
            points[i] = translate(points[i],CENTER)

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