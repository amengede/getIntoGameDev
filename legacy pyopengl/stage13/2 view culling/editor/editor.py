import PyQt6
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QGridLayout, QPushButton,
    QFileDialog
)
from PyQt6.QtGui import (
    QAction, QPainter, QColor, QFont, QIcon, 
    QPixmap
)
from PyQt6.QtCore import (
    QSize, QPointF, QRect
)

import sys

BRUSHES = ["Walls", "Doors", "Floors", "Ceilings", "Player"]

GEOMETRY = 0
FLOOR = 1
CEILING = 2
THINGS = 3

"""
File format:
size rows cols
geometry
...
floors
...
ceilings
...
things
player x y
"""

class Map:


    def __init__(self):
        """
            geometry: dict[tuple(int,int), Wall/Door object]
            floors: dict[tuple(int,int), Floor object]
            ceilings: dict[tuple(int,int), Ceiling object]
            player: Player object
        """

        self.geometry = {}
        self.floors = {}
        self.ceilings = {}
        self.player = None

        self.x_min = 0
        self.x_max = 0
        self.y_min = 0
        self.y_max = 0
        self.rows = 1
        self.cols = 1
    
    def remember_position(self, position):

        x = position[0]
        y = position[1]

        self.x_min = min(x, self.x_min)
        self.x_max = max(x, self.x_max)
        self.y_min = min(y, self.y_min)
        self.y_max = max(y, self.y_max)
        self.rows = self.y_max - self.y_min + 1
        self.cols = self.x_max - self.x_min + 1

    def add_wall(self, position, index):

        self.remember_position(position)

        self.remember_position(position)

        self.geometry[position] = index

        self.remove_floor(position)
        
        self.remove_ceiling(position)

        self.remove_player(position)
    
    def add_door(self, position):

        self.remember_position(position)

        self.geometry[position] = "d"

        self.remove_floor(position)
        
        self.remove_ceiling(position)

        self.remove_player(position)

    def add_floor(self, position, index):

        self.remember_position(position)

        self.remove_geometry(position)

        self.floors[position] = index

    def add_ceiling(self, position, index):

        self.remember_position(position)

        self.remove_geometry(position)
        
        self.ceilings[position] = index

    def add_player(self, position):

        self.remember_position(position)

        self.remove_geometry(position)

        self.player = position

    def remove_geometry(self, position):

        if position in self.geometry:
            self.geometry.pop(position)

    def remove_floor(self, position):

        if position in self.floors:
            self.floors.pop(position)

    def remove_ceiling(self, position):

        if position in self.ceilings:
            self.ceilings.pop(position)

    def remove_player(self, position):

        if self.player is None:
            return

        if (position[0] == self.player[0] and position[1] == self.player[1]):
            self.player = None

    def save(self, filename):

        with open(filename, "w") as file:

            self.save_size(file)

            self.save_geometry(file)

            self.save_floors(file)

            self.save_ceilings(file)

            self.save_things(file)
    
    def save_size(self, file):

        file.write(f"size {self.rows} {self.cols}\n")
    
    def save_geometry(self, file):

        file.write("geometry\n")

        self.save_array(file, self.geometry)
    
    def save_floors(self, file):

        file.write("floors\n")

        self.save_array(file, self.floors)
    
    def save_ceilings(self, file):

        file.write("ceilings\n")

        self.save_array(file, self.ceilings)
    
    def save_array(self, file, src: dict):

        data = [["0" for j in range(self.cols)] for i in range(self.rows)]
        
        for (position, entry) in src.items():
            if entry == "d":
                parsed_entry = "d"
            else:
                parsed_entry = str(int(entry) + 1)
            i = position[1] - self.y_min
            j = position[0] - self.x_min
            print(f"rows: {self.rows}, columns: {self.cols}")
            print(f"Original: ({position[1]}, {position[0]}), shifted: ({i}, {j})")
            data[position[1] - self.y_min]\
                [position[0] - self.x_min] = parsed_entry

        for y in range(self.rows):
            for x in range(self.cols):
                file.write(data[y][x])
                file.write(" ")
            file.write("\n")
    
    def save_things(self, file):

        file.write(f"things\n")
        if self.player is not None:
            file.write(f"player {self.player[0]} {self.player[1]}")
    
    def load(self, filename):

        self.geometry = {}
        self.floors = {}
        self.ceilings = {}
        self.player = None

        with open(filename, "r") as file:

            self.load_size(file)

            self.load_geometry(file)

            self.load_floors(file)

            self.load_ceilings(file)

            self.load_things(file)
    
    def load_size(self, file):

        line = file.readline().replace("\n","")
        line = line.split(" ")
        self.rows = int(line[1])
        self.cols = int(line[2])
        self.x_min = 0
        self.y_min = 0
        self.x_max = self.cols - 1
        self.y_max = self.rows - 1
    
    def load_geometry(self, file):

        file.readline()

        self.load_array(file, self.geometry)
    
    def load_floors(self, file):

        file.readline()

        self.load_array(file, self.floors)
    
    def load_ceilings(self, file):

        file.readline()

        self.load_array(file, self.ceilings)
    
    def load_array(self, file, src):

        for y in range(self.rows):
            line = file.readline().replace("\n","")
            line = line.split(" ")
            for x in range(self.cols):

                if line[x] == "0":
                    continue
                
                if line[x] == "d":
                    parsed_entry = "d"
                else:
                    parsed_entry = str(int(line[x]) - 1)
                
                src[(x,y)] = parsed_entry
    
    def load_things(self, file):

        line = file.readline()
        while line:
            line = line.replace("\n","")
            line = line.split(" ")
            if line[0] == "player":
                self.player = (int(line[1]),int(line[2]))
            line = file.readline()
    
class Editor(QMainWindow):


    def __init__(self):

        super().__init__()

        self.setWindowTitle("Level Editor")

        self.createMenu()

        self.MakeWidgetsAndLayouts()

        self.connectWidgets()

        self.camera_pos = (0,0)

        self.brush_index = 0
        self.wall_index = 0
        self.door_index = 0
        self.floor_index = 0
        self.ceiling_index = 0

        self.populateFunctions = [
            self.populateWallProperties,
            self.populateDoorProperties,
            self.populateFloorProperties,
            self.populateCeilingProperties,
            self.populatePlayerProperties
        ]

        self.DOOR_IMAGES = [
            QPixmap("gfx/textures/doors/door02_7.jpg","jpg"),
        ]

        self.FLOOR_IMAGES = [
            QPixmap("gfx/textures/floors/plat_top2.jpg","jpg"),
            QPixmap("gfx/textures/floors/sfloor1_2.jpg","jpg"),
            QPixmap("gfx/textures/floors/sfloor4_2.jpg","jpg"),
            QPixmap("gfx/textures/floors/sfloor4_4.jpg","jpg"),
            QPixmap("gfx/textures/floors/sfloor4_6.jpg","jpg"),
            QPixmap("gfx/textures/floors/sfloor4_7.jpg","jpg")
        ]

        self.WALL_IMAGES = [
            QPixmap("gfx/textures/walls/comp1_1.jpg","jpg"),
            QPixmap("gfx/textures/walls/tech01_2.jpg","jpg"),
            QPixmap("gfx/textures/walls/tech01_7.jpg","jpg"),
            QPixmap("gfx/textures/walls/tech08_1.jpg","jpg"),
            QPixmap("gfx/textures/walls/tech09_3.jpg","jpg"),
            QPixmap("gfx/textures/walls/twall2_6.jpg","jpg")
        ]

        self.newMap()

        self.populateFunctions[self.brush_index]()
    
    def createMenu(self):

        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu("File")

        self.new_map_button = QAction("New", self)
        self.new_map_button.triggered.connect(self.newMap)
        self.file_menu.addAction(self.new_map_button)

        self.save_map_button = QAction("Save", self)
        self.save_map_button.triggered.connect(self.saveMap)
        self.file_menu.addAction(self.save_map_button)

        self.load_map_button = QAction("Load", self)
        self.load_map_button.triggered.connect(self.loadMap)
        self.file_menu.addAction(self.load_map_button)
    
    def newMap(self):

        self.map = Map()
        self.map_container.repaint()
    
    def saveMap(self):

        filename = QFileDialog.getSaveFileName(self)
        if len(filename[0]) > 0:
            self.map.save(filename[0])
        self.map_container.repaint()
    
    def loadMap(self):

        filename = QFileDialog.getOpenFileName(self)
        if len(filename[0]) > 0:
            self.map.load(filename[0])
        self.map_container.repaint()

    def MakeWidgetsAndLayouts(self):

        #make elements
        self.left_frame = QWidget()
        self.left_layout = QVBoxLayout()
        self.right_frame = QWidget()
        self.right_layout = QVBoxLayout()
        self.main_widget = QWidget()

        self.map_container = MapContainer(width=1000, height=1000, parent = self)
        self.type_selector = TypeSelector(width = 200, height = 50)
        self.property_editor = PropertyEditor(width = 200, height = 800)
        self.map_controller = MapController(width = 150, height = 150)

        #define layouts
        self.left_layout.addWidget(self.map_container)

        self.right_layout.addWidget(self.type_selector)
        self.right_layout.addWidget(self.property_editor)
        self.right_layout.addWidget(self.map_controller)

        self.left_frame.setLayout(self.left_layout)
        self.right_frame.setLayout(self.right_layout)
        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.left_frame)
        self.main_layout.addWidget(self.right_frame)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

    def connectWidgets(self):

        self.type_selector.left_brush_button.clicked.connect(self.selectLeftBrush)
        self.type_selector.right_brush_button.clicked.connect(self.selectRightBrush)

        self.map_controller.move_left_button.clicked.connect(self.moveLeft)
        self.map_controller.move_right_button.clicked.connect(self.moveRight)
        self.map_controller.move_up_button.clicked.connect(self.moveUp)
        self.map_controller.move_down_button.clicked.connect(self.moveDown)

    def selectLeftBrush(self):

        self.brush_index = (self.brush_index - 1) % len(BRUSHES)

        self.type_selector.label.setText(BRUSHES[self.brush_index])

        self.populateFunctions[self.brush_index]()
    
    def selectRightBrush(self):

        self.brush_index = (self.brush_index + 1) % len(BRUSHES)

        self.type_selector.label.setText(BRUSHES[self.brush_index])

        self.populateFunctions[self.brush_index]()
    
    def clearLayout(self, widget):

        while widget.layout.count() != 0:
            child = widget.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def populateWallProperties(self):

        self.clearLayout(self.property_editor)

        wallSelector = ImageSelector(200, 200, self.WALL_IMAGES[self.wall_index])
        wallSelector.left_button.clicked.connect(self.leftWall)
        wallSelector.right_button.clicked.connect(self.rightWall)

        self.property_editor.layout.addWidget(wallSelector)

    def populateDoorProperties(self):

        self.clearLayout(self.property_editor)

        doorSelector = ImageSelector(200, 200, self.DOOR_IMAGES[self.door_index])
        doorSelector.left_button.clicked.connect(self.leftDoor)
        doorSelector.right_button.clicked.connect(self.rightDoor)

        self.property_editor.layout.addWidget(doorSelector)
    
    def populateFloorProperties(self):

        self.clearLayout(self.property_editor)

        floorSelector = ImageSelector(200, 200, self.FLOOR_IMAGES[self.floor_index])
        floorSelector.left_button.clicked.connect(self.leftFloor)
        floorSelector.right_button.clicked.connect(self.rightFloor)

        self.property_editor.layout.addWidget(floorSelector)
    
    def populateCeilingProperties(self):

        self.clearLayout(self.property_editor)

        ceilingSelector = ImageSelector(200, 200, self.FLOOR_IMAGES[self.ceiling_index])
        ceilingSelector.left_button.clicked.connect(self.leftCeiling)
        ceilingSelector.right_button.clicked.connect(self.rightCeiling)

        self.property_editor.layout.addWidget(ceilingSelector)
    
    def populatePlayerProperties(self):

        self.clearLayout(self.property_editor)

        label = QLabel("Player Properties")

        self.property_editor.layout.addWidget(label)
    
    def moveLeft(self):

        self.camera_pos = (self.camera_pos[0] - 1, self.camera_pos[1])
        self.map_container.repaint()
    
    def moveRight(self):

        self.camera_pos = (self.camera_pos[0] + 1, self.camera_pos[1])
        self.map_container.repaint()
    
    def moveUp(self):

        self.camera_pos = (self.camera_pos[0], self.camera_pos[1] - 1)
        self.map_container.repaint()
    
    def moveDown(self):

        self.camera_pos = (self.camera_pos[0], self.camera_pos[1] + 1)
        self.map_container.repaint()
    
    def leftWall(self):
        self.wall_index = (self.wall_index - 1) % len(self.WALL_IMAGES)
        self.populateWallProperties()
    
    def rightWall(self):
        self.wall_index = (self.wall_index + 1) % len(self.WALL_IMAGES)
        self.populateWallProperties()
    
    def leftDoor(self):

        self.door_index = (self.door_index - 1) % len(self.DOOR_IMAGES)
        self.populateDoorProperties()
    
    def rightDoor(self):

        self.door_index = (self.door_index + 1) % len(self.DOOR_IMAGES)
        self.populateDoorProperties()
    
    def leftFloor(self):

        self.floor_index = (self.floor_index - 1) % len(self.FLOOR_IMAGES)
        self.populateFloorProperties()
    
    def rightFloor(self):

        self.floor_index = (self.floor_index + 1) % len(self.FLOOR_IMAGES)
        self.populateFloorProperties()
    
    def leftCeiling(self):

        self.ceiling_index = (self.ceiling_index - 1) % len(self.FLOOR_IMAGES)
        self.populateCeilingProperties()
    
    def rightCeiling(self):

        self.ceiling_index = (self.ceiling_index + 1) % len(self.FLOOR_IMAGES)
        self.populateCeilingProperties()
    
    def click(self, action, viewType):

        position = (
            self.camera_pos[0] + int(action.position().x() // 24),
            self.camera_pos[1] + int(action.position().y() / 24)
        )

        if (str(action.button()) == "MouseButton.LeftButton"):
            leftClick = True
        else:
            leftClick = False
        
        if leftClick:
            if viewType == GEOMETRY:
                if self.brush_index == 0:
                    self.map.add_wall(position, self.wall_index)
                elif self.brush_index == 1:
                    self.map.add_door(position)
            elif viewType == FLOOR and self.brush_index == 2:
                self.map.add_floor(position, self.floor_index)
            elif viewType == CEILING and self.brush_index == 3:
                self.map.add_ceiling(position, self.ceiling_index)
            elif viewType == THINGS:
                if self.brush_index == 4:
                    self.map.add_player(position)
        else:
            if viewType == GEOMETRY:
                if self.brush_index == 0 or self.brush_index == 1:
                    self.map.remove_geometry(position)
            elif viewType == FLOOR and self.brush_index == 2:
                self.map.remove_floor(position)
            elif viewType == CEILING and self.brush_index == 3:
                self.map.remove_ceiling(position)
            elif viewType == THINGS:
                if self.brush_index == 4:
                    self.map.remove_player(position)
        
        self.map_container.repaint()
    
class MapContainer(QWidget):

    def __init__(self, width, height, parent):

        super().__init__()

        self.geometryView = MapView(
            width = width // 2, height = height//2, 
            title = "Geometry", parent = parent,
            viewType = GEOMETRY
        )
        self.floorView = MapView(
            width = width // 2, height = height//2, 
            title = "Floor", parent = parent,
            viewType = FLOOR
        )
        self.ceilingView = MapView(
            width = width // 2, height = height//2, 
            title = "Ceiling", parent = parent,
            viewType = CEILING
        )
        self.thingView = MapView(
            width = width // 2, height = height//2, 
            title = "Objects", parent = parent,
            viewType = THINGS
        )

        self.layout = QGridLayout()
        self.layout.addWidget(self.geometryView,0,0)
        self.layout.addWidget(self.floorView,0,1)
        self.layout.addWidget(self.ceilingView,1,0)
        self.layout.addWidget(self.thingView,1,1)

        self.setLayout(self.layout)

class MapView(QWidget):

    
    def __init__(self, width, height, **kwargs):

        super().__init__()

        self.width = width
        self.height = height

        self.setFixedSize(QSize(width, height))

        if "color" in kwargs:
            self.color = kwargs["color"]
        else:
            self.color = QColor("black")
        
        if "title" in kwargs:
            self.title = kwargs["title"]
        else:
            self.title = "Window"
        
        if "parent" in kwargs:
            self.parent = kwargs["parent"]
        else:
            self.parent = None
        
        if "viewType" in kwargs:
            self.viewType = kwargs["viewType"]
        else:
            self.viewType = GEOMETRY
    
    def mousePressEvent(self, event):
        self.parent.click(event, self.viewType)
    
    def paintEvent(self, event):

        if self.parent is not None:
            camera_pos = self.parent.camera_pos
        else:
            camera_pos = (0,0)
        
        rect = event.rect()
        painter = QPainter(self)
        painter.fillRect(rect, self.color)

        self.draw_walls(painter, camera_pos)
        self.draw_floors(painter, camera_pos)
        self.draw_ceilings(painter, camera_pos)
        self.draw_things(painter, camera_pos)

        painter.setPen(QColor(128,128,128,255))
        painter.setFont(QFont("Helvetica", 6))

        for x in range(0, self.width, 24):
            painter.setPen(QColor(128,128,128,255))
            painter.drawLine(QPointF(x,0), QPointF(x,self.height))
            painter.setPen(QColor("white"))
            painter.drawText(QPointF(x + 4,self.height - 8), str(camera_pos[0] + x//24))
        
        for y in range(0, self.height, 24):
            painter.setPen(QColor(128,128,128,255))
            painter.drawLine(QPointF(0,y), QPointF(self.width,y))
            painter.setPen(QColor("white"))
            painter.drawText(QPointF(4,y + 8), str(camera_pos[1] + y//24))
        
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Helvetica", 12))
        painter.drawText(QPointF(10,20), self.title)
    
    def draw_walls(self, painter, camera_pos):

        for (position,entry) in self.parent.map.geometry.items():

            rect = QRect(
                24 * (position[0] - camera_pos[0]), 
                24 * (position[1] - camera_pos[1]), 
                24, 24
            )

            if self.viewType == GEOMETRY:

                if (entry == "d"):
                    texture = self.parent.DOOR_IMAGES[0]
                else:
                    texture = self.parent.WALL_IMAGES[int(entry)]
                
                painter.drawPixmap(rect, texture)
            
            else:

                painter.fillRect(rect, QColor(64, 0, 0, 255))
    
    def draw_floors(self, painter, camera_pos):

        for (position,entry) in self.parent.map.floors.items():

            rect = QRect(
                24 * (position[0] - camera_pos[0]), 
                24 * (position[1] - camera_pos[1]), 
                24, 24
            )

            if self.viewType == FLOOR or self.viewType == THINGS:

                texture = self.parent.FLOOR_IMAGES[int(entry)]
                
                painter.drawPixmap(rect, texture)
            
            elif self.viewType == GEOMETRY:

                painter.fillRect(rect, QColor(64, 0, 0, 255))

    def draw_ceilings(self, painter, camera_pos):

        for (position,entry) in self.parent.map.ceilings.items():

            rect = QRect(
                24 * (position[0] - camera_pos[0]), 
                24 * (position[1] - camera_pos[1]), 
                24, 24
            )

            if self.viewType == CEILING:

                texture = self.parent.FLOOR_IMAGES[int(entry)]
                
                painter.drawPixmap(rect, texture)
            
            elif self.viewType == GEOMETRY:

                painter.fillRect(rect, QColor(64, 0, 0, 255))
    
    def draw_things(self, painter, camera_pos):

        if self.parent.map.player is not None:

            rect = QRect(
                24 * (self.parent.map.player[0] - camera_pos[0]), 
                24 * (self.parent.map.player[1] - camera_pos[1]), 
                24, 24
            )

            if self.viewType == THINGS:
                
                painter.setPen(QColor(0,128,0,255))
                painter.setFont(QFont("Helvetica", 6))
                painter.drawText(QPointF(
                    24 * (self.parent.map.player[0] - camera_pos[0]) + 8,
                    24 * (self.parent.map.player[1] - camera_pos[1]) + 14
                ), "P")
                painter.drawEllipse(rect)
            
            elif self.viewType == GEOMETRY:

                painter.fillRect(rect, QColor(64, 0, 0, 255))

class TypeSelector(QWidget):

    
    def __init__(self, width, height):

        super().__init__()

        self.setFixedSize(QSize(width, height))

        self.layout = QHBoxLayout()
        self.left_brush_button = QPushButton(QIcon(QPixmap("gfx/left-arrow.png", "png")),"")
        self.label = QLabel(BRUSHES[0])
        self.right_brush_button = QPushButton(QIcon(QPixmap("gfx/right-arrow.png", "png")),"")
        self.layout.addWidget(self.left_brush_button)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.right_brush_button)
        self.setLayout(self.layout)

class MapController(QWidget):

    
    def __init__(self, width, height):

        super().__init__()

        self.setFixedSize(QSize(width, height))

        self.layout = QGridLayout()

        self.move_up_button = QPushButton(QIcon(QPixmap("gfx/up-arrow.png", "png")),"")
        self.move_down_button = QPushButton(QIcon(QPixmap("gfx/down-arrow.png", "png")),"")
        self.move_left_button = QPushButton(QIcon(QPixmap("gfx/left-arrow.png", "png")),"")
        self.move_right_button = QPushButton(QIcon(QPixmap("gfx/right-arrow.png", "png")),"")

        self.layout.addWidget(self.move_up_button, 0, 1)
        self.layout.addWidget(self.move_left_button, 1, 0)
        self.layout.addWidget(self.move_right_button, 1, 2)
        self.layout.addWidget(self.move_down_button, 2, 1)
        self.setLayout(self.layout)

class PropertyEditor(QWidget):

    
    def __init__(self, width, height):

        super().__init__()

        self.setFixedSize(QSize(width, height))

        self.layout = QVBoxLayout()
        label = QLabel("Test")
        self.layout.addWidget(label)
        self.setLayout(self.layout)

class ImageSelector(QWidget):


    def __init__(self, width, height, image):

        super().__init__()

        self.setFixedSize(QSize(width, height))

        self.imageFrame = ImageFrame(width, height - 50, image)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.imageFrame)

        self.buttonLayout = QHBoxLayout()
        self.buttonContainer = QWidget()
        self.left_button = QPushButton(QIcon(QPixmap("gfx/left-arrow.png", "png")),"")
        self.right_button = QPushButton(QIcon(QPixmap("gfx/right-arrow.png", "png")),"")
        self.buttonLayout.addWidget(self.left_button)
        self.buttonLayout.addWidget(self.right_button)
        self.buttonContainer.setLayout(self.buttonLayout)
        self.layout.addWidget(self.buttonContainer)

        self.setLayout(self.layout)

class ImageFrame(QWidget):


    def __init__(self, width, height, image):

        super().__init__()

        self.image = image

        self.setFixedSize(QSize(width, height))
    
    def paintEvent(self, event):
        
        rect = event.rect()
        painter = QPainter(self)
        painter.drawPixmap(rect, self.image)

app = QApplication(sys.argv)

window = Editor()
window.show()

app.exec()