from config import *
import piece

class GameBoard:

    TYPES = ["red", "orange", "pink", "blue", "green"]

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
        self.reset()
        self.populate()
    
    def update(self):
        #reset state of pieces
        for row in range(self.numRows):
            for column in range(self.numCols):
                self.pieces[row][column].setMouseHover(False)
                self.pieces[row][column].setNeighbor(False)
        
        self.handleMouseMovement()
        if self.selectedPiece is not None:
            self.selectedPiece.setMouseHover(True)
            for piece in self.getNeighbors(self.selectedPiece):
                piece.setNeighbor(True)
    
    def hasMouse(self, x, y):
        return (x > self.x and x < self.x + self.width and y > self.y and y < self.y + self.height)

    def cartesianToGrid(self, x, y):
        row = max(0,min(self.numRows - 1,(y - self.y)//PIECE_SIZE))
        column = max(0,min(self.numCols - 1,(x - self.x)//PIECE_SIZE))
        return (row,column)
    
    def handleMouseMovement(self):
        (x,y) = pg.mouse.get_pos()
        if self.hasMouse(x,y):
            (row,column) = self.cartesianToGrid(x,y)
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
        if row > 0:
            neighbors.append(self.pieces[row - 1][column])
        if row < self.numRows - 1:
            neighbors.append(self.pieces[row + 1][column])
        if column > 0:
            neighbors.append(self.pieces[row][column - 1])
        if column < self.numCols - 1:
            neighbors.append(self.pieces[row][column + 1])
        return neighbors
    
    def reset(self):
        for row in range(self.numRows):
            self.pieces.append([])
            for column in range(self.numCols):
                self.pieces[row].append(None)
    
    def populate(self):
        for row in range(self.numRows):
            for column in range(self.numCols):
                x = column*PIECE_SIZE
                y = row*PIECE_SIZE
                type = GameBoard.TYPES[random.randint(0,4)]
                self.pieces[row][column] = piece.CandyPiece(x,y,type)
                
    def draw(self, surface):
        self.surface.fill(PALETTE["yellow"])
        for row in range(self.numRows):
            for column in range(self.numCols):
                if self.pieces[row][column] != None:
                    self.pieces[row][column].draw(self.surface)
        surface.blit(self.surface,(self.x,self.y))