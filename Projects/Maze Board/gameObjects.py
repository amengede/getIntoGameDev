from config import *
from assets import *
import math

class GameBoard:
    def __init__(self,layout):
        self.walls = []
        for row in range(10):
            self.walls.append([])
            for col in range(10):
                self.walls[row].append(None)
                if layout[row][col] != 0:
                    if layout[row][col] == 2:
                        self.ball = Ball((32*col) - 160 + 8,(32*row) - 160 + 8,self)
                    else:
                        self.walls[row][col] = Wall((32*col) - 160,(32*row) - 160,self)


        self.rot_x = 0
        self.rot_y = 0
        self.max_x_rotation = 0.5
        self.max_y_rotation = 0.5

        self.keyMap = {1:(1,0),
                        2:(-1,0),
                        4:(0,1),5:(1,1),6:(-1,1),7:(0,1),
                        8:(0,-1),9:(1,-1),10:(-1,-1),11:(0,-1),13:(1,0),14:(-1,0)}
    
    def collideWall(self,x,y):
        xGrid = math.floor(x/32 + 5)
        yGrid = math.floor(y/32 + 5)
        biggest = max(xGrid,yGrid)
        smallest = min(xGrid,yGrid)
        if biggest > 9 or smallest < 0:
            return True
        if self.walls[yGrid][xGrid] != None:
            return True
        return False
    
    def update(self):
        #compute rotation matrix
        rot_x_m = pyrr.Matrix44.from_x_rotation(self.rot_x)
        rot_y_m = pyrr.Matrix44.from_y_rotation(self.rot_y)
        self.rotationMatrix = pyrr.matrix44.multiply(rot_x_m,rot_y_m)

        self.ball.update()

        for row in self.walls:
            for wall in row:
                if wall != None:
                    wall.update()

    def handleKeys(self,key):
        if key in self.keyMap:
            angleIncrement = self.keyMap[key]
            self.rot_x += 0.01*angleIncrement[0]
            if self.rot_x >= self.max_x_rotation:
                self.rot_x = self.max_x_rotation
            elif self.rot_x <= -self.max_x_rotation:
                self.rot_x = -self.max_x_rotation
            self.rot_y += 0.01*angleIncrement[1]
            if self.rot_y >= self.max_y_rotation:
                self.rot_y = self.max_y_rotation
            elif self.rot_y <= -self.max_y_rotation:
                self.rot_y = -self.max_y_rotation
    
    def draw(self):
        #glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glUniformMatrix4fv(MODEL_LOC,1,GL_FALSE,self.rotationMatrix)
        glBindVertexArray(BOARD_MODEL.getVAO())
        glBindTexture(GL_TEXTURE_2D,BOARD.getTexture())
        glDrawArrays(GL_TRIANGLES,0,BOARD_MODEL.getVertexCount())

        self.ball.draw()

        for row in self.walls:
            for wall in row:
                if wall != None:
                    wall.draw()

class Wall:
    def __init__(self,x,y,parent):
        self.parent = parent
        self.x = x
        self.y = y
        self.z = 0
    
    def update(self):
        #first translate to position on board, then rotate with the board
        translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([self.x,self.y,self.z]))
        self.model = pyrr.matrix44.multiply(translation,self.parent.rotationMatrix)
    
    def draw(self):
        glUniformMatrix4fv(MODEL_LOC,1,GL_FALSE,self.model)
        glBindVertexArray(WALL_MODEL.getVAO())
        glBindTexture(GL_TEXTURE_2D,WALL.getTexture())
        glDrawArrays(GL_TRIANGLES,0,WALL_MODEL.getVertexCount())

class Ball:
    def __init__(self,x,y,parent):
        self.parent = parent
        self.x = x
        self.y = y
        self.z = 0
        self.velocity = [0,0]
    
    def update(self):
        #first translate to position on board, then rotate with the board
        translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([self.x,self.y,self.z]))
        self.model = pyrr.matrix44.multiply(translation,self.parent.rotationMatrix)
        acceleration = [-0.1*self.parent.rot_y,0.1*self.parent.rot_x]
        self.velocity[0] += acceleration[0]
        self.velocity[1] += acceleration[1]
        testX = self.x + self.velocity[0] + 8*np.sign(self.velocity[0])
        testY = self.y + self.velocity[1] + 8*np.sign(self.velocity[1])
        #check x direction
        if self.parent.collideWall(testX,self.y):
            self.velocity[0] *= -0.25
        #check y direction
        if self.parent.collideWall(self.x,testY):
            self.velocity[1] *= -0.25
        self.x += self.velocity[0]
        self.y += self.velocity[1]
    
    def draw(self):
        glUniformMatrix4fv(MODEL_LOC,1,GL_FALSE,self.model)
        glBindVertexArray(BALL_MODEL.getVAO())
        glBindTexture(GL_TEXTURE_2D,BALL.getTexture())
        glDrawArrays(GL_TRIANGLES,0,BALL_MODEL.getVertexCount())