from typing import NewType
from config import *
import queue
import piece
import math

class GameBoard:

    TYPES = ["red", "orange", "pink", "blue", "green"]

    STABLE = 0
    SHAKE = 1

    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.width = 200
        self.height = 380
        self.surface = pg.Surface((self.width,self.height))
        self.numRows = self.height//PIECE_SIZE
        self.numCols = self.width//PIECE_SIZE
        self.pieces = []
        self.selectedPiece = None
        self.reset(self.pieces)
        self.populate(self.pieces)
        self.state = GameBoard.STABLE
        self.shake_t = 0
        self.x_offset = 0
    
    def update(self):
        scoreIncrease = 0
        #reset state of pieces
        for row in range(self.numRows):
            for column in range(self.numCols):
                thisPiece = self.pieces[row][column]
                if thisPiece is not None:
                    thisPiece.setMouseHover(False)
                    thisPiece.setNeighbor(False)
                    thisPiece.setSmashed(False)
                    thisPiece.update()
        
        self.handleMouseMovement()
        if self.selectedPiece is not None:
            self.selectedPiece.setMouseHover(True)
            for thisPiece in self.getNeighbors(self.selectedPiece):
                thisPiece.setNeighbor(True)
        if self.isStable() and self.state == GameBoard.STABLE:
            scoreIncrease += self.search()
            self.clean()
        elif self.state == GameBoard.SHAKE:
            self.shake()
        return scoreIncrease
        
    def search(self):
        scoreIncrease = 0
        for row in range(self.numRows):
            for column in range(self.numCols):
                firstPiece = self.pieces[row][column]
                if firstPiece is not None:
                    searched = []
                    streak = [firstPiece,]
                    toSearch = queue.Queue()
                    toSearch.put(firstPiece)
                    while not toSearch.empty():
                        thisPiece = toSearch.get()
                        matches = self.expandSearch(thisPiece)
                        searched.append(thisPiece)
                        for match in matches:
                            if not match in searched:
                                toSearch.put(match)
                                streak.append(match)
                    if len(streak) > 3:
                        scoreIncrease += len(streak)
                        self.state = GameBoard.SHAKE
                        for thisPiece in streak:
                            thisPiece.setSmashed(True)
        return scoreIncrease
    
    def expandSearch(self,piece):
        result = []
        candidates = self.getNeighbors(piece)
        for candidate in candidates:
            if candidate.type == piece.type:
                result.append(candidate)
        return result
    
    def allowableTypes(self,row,column):
        result = []
        for type in GameBoard.TYPES:
            x = column * PIECE_SIZE
            y = row * PIECE_SIZE
            firstPiece = piece.CandyPiece(x,y,type)
            searched = []
            streak = [firstPiece,]
            toSearch = queue.Queue()
            toSearch.put(firstPiece)
            while not toSearch.empty():
                thisPiece = toSearch.get()
                matches = self.expandSearch(thisPiece)
                searched.append(thisPiece)
                for match in matches:
                    if not match in searched:
                        toSearch.put(match)
                        streak.append(match)
            if len(streak) <= 3:
                result.append(type)
        return result
    
    def isStable(self):
        for row in range(self.numRows):
            for column in range(self.numCols):
                thisPiece = self.pieces[row][column]
                if (thisPiece is not None) and (not thisPiece.isStable()):
                    return False
        return True
    
    def shake(self):
        self.x_offset = 32*math.sin(self.shake_t**2)/(self.shake_t + 1)
        self.shake_t += 1
        if self.shake_t > 10*math.pi:
            self.state = GameBoard.STABLE
            self.shake_t = 0
            self.x_offset = 0
    
    def clean(self):
        for row in range(self.numRows):
            for column in range(self.numCols):
                if self.pieces[row][column] is not None and self.pieces[row][column].smashed:
                    self.pieces[row][column] = None
        #take snapshot of board state
        oldBoard = []
        self.reset(oldBoard)
        self.populate(oldBoard,self.pieces)
        self.reset(self.pieces)
        #check how far each piece must move down
        for column in range(self.numCols):
            columnGaps = 0
            for row in range(self.numRows):

                dropCount = 0
                for rowBelow in range(row, self.numRows):
                    if oldBoard[rowBelow][column] is None:
                        dropCount += 1
                columnGaps = max(columnGaps,dropCount)

                thisPiece = oldBoard[row][column]
                if thisPiece is not None:
                    currentY = thisPiece.y
                    newY = currentY + dropCount * PIECE_SIZE
                    self.pieces[row + dropCount][column] = thisPiece
                    thisPiece.setGroundY(newY)
            #fill gaps at top
            for row in range(columnGaps):
                x = column * PIECE_SIZE
                y = row * PIECE_SIZE - columnGaps * PIECE_SIZE
                targetY = row * PIECE_SIZE
                allowableTypes = self.allowableTypes(row,column)
                type = allowableTypes[random.randint(0,len(allowableTypes) - 1)]
                thisPiece = piece.CandyPiece(x,y,type)
                thisPiece.setGroundY(targetY)
                self.pieces[row][column] = thisPiece
        
    def hasMouse(self, x, y):
        return (x > self.x and x < self.x + self.width and y > self.y and y < self.y + self.height)

    def cartesianToGrid(self, x, y):
        row = max(0,min(self.numRows - 1,int(y - self.y)//PIECE_SIZE))
        column = max(0,min(self.numCols - 1,int(x - self.x)//PIECE_SIZE))
        return (row,column)
    
    def handleMouseMovement(self):
        (x,y) = pg.mouse.get_pos()
        if self.hasMouse(x,y):
            (row,column) = self.cartesianToGrid(x,y)
            if self.pieces[row][column] is not None:
                self.pieces[row][column].setMouseHover(True)
    
    def handleMouseClick(self):
        (x,y) = pg.mouse.get_pos()
        if self.hasMouse(x,y):
            (row,column) = self.cartesianToGrid(x,y)
            if self.selectedPiece is None:
                self.selectedPiece = self.pieces[row][column]
            else:
                newPiece = self.pieces[row][column]
                if newPiece in self.getNeighbors(self.selectedPiece):
                    #swap types
                    temp = self.selectedPiece.type
                    self.selectedPiece.type = newPiece.type
                    newPiece.type = temp
                    self.selectedPiece = None
                else:
                    self.selectedPiece = newPiece

    def getNeighbors(self, piece):
        (x,y) = piece.getCartesian()
        (row,column) = self.cartesianToGrid(x + self.x, y + self.y)
        neighbors = []
        if row > 0 and self.pieces[row - 1][column] is not None:
            neighbors.append(self.pieces[row - 1][column])
        if row < self.numRows - 1 and self.pieces[row + 1][column] is not None:
            neighbors.append(self.pieces[row + 1][column])
        if column > 0 and self.pieces[row][column - 1] is not None:
            neighbors.append(self.pieces[row][column - 1])
        if column < self.numCols - 1 and self.pieces[row][column + 1] is not None:
            neighbors.append(self.pieces[row][column + 1])
        return neighbors
    
    def reset(self,board):
        if len(board) == 0:
            for row in range(self.numRows):
                board.append([])
                for column in range(self.numCols):
                    board[row].append(None)
        else:
            for row in range(self.numRows):
                for column in range(self.numCols):
                    board[row][column] = None
    
    def populate(self,board,boardToCopy=None):
        for row in range(self.numRows):
            for column in range(self.numCols):
                if boardToCopy is None:
                    x = column*PIECE_SIZE
                    y = row*PIECE_SIZE
                    allowableTypes = self.allowableTypes(row,column)
                    type = allowableTypes[random.randint(0,len(allowableTypes) - 1)]
                    board[row][column] = piece.CandyPiece(x,y,type)
                else:
                    board[row][column] = boardToCopy[row][column]
                
    def draw(self, surface):
        self.surface.fill(PALETTE["yellow"])
        for row in range(self.numRows):
            for column in range(self.numCols):
                if self.pieces[row][column] is not None:
                    self.pieces[row][column].draw(self.surface, self.x_offset)
        surface.blit(self.surface,(self.x,self.y))