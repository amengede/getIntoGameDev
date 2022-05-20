from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QPushButton
)
from PyQt6.QtGui import (
    QAction, QPainter, QColor, QFont, QIcon, QPixmap
)
from PyQt6.QtCore import (
    QSize, QPointF
)
import sys

BRUSHES = ["Walls", "Doors", "Floors", "Ceilings", "Player"]

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

class Editor(QMainWindow):


    def __init__(self):

        super().__init__()

        self.setWindowTitle("Level Editor")

        self.createMenu()

        self.MakeWidgetsAndLayouts()

        self.camera_pos = (0,0)

        self.newMap()
    
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
    
    def saveMap(self):

        print("save map")
    
    def loadMap(self):

        print("load map")

    def MakeWidgetsAndLayouts(self):

        #make elements
        self.left_frame = QWidget()
        self.left_layout = QVBoxLayout()
        self.right_frame = QWidget()
        self.right_layout = QVBoxLayout()
        self.main_widget = QWidget()

        self.map_container = MapContainer(width=1000, height=1000)
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

class MapContainer(QWidget):

    def __init__(self, width, height):

        super().__init__()

        self.geometryView = MapView(
            width = width // 2, height = height//2, 
            title = "Geometry"
        )
        self.floorView = MapView(
            width = width // 2, height = height//2, 
            title = "Floor"
        )
        self.ceilingView = MapView(
            width = width // 2, height = height//2, 
            title = "Ceiling"
        )
        self.thingView = MapView(
            width = width // 2, height = height//2, 
            title = "Objects"
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
    
    def paintEvent(self, event):
        
        rect = event.rect()
        painter = QPainter(self)
        painter.fillRect(rect, self.color)

        painter.setPen(QColor(128,128,128,255))
        painter.setFont(QFont("Helvetica", 6))

        for x in range(0, self.width, 24):
            painter.setPen(QColor(128,128,128,255))
            painter.drawLine(QPointF(x,0), QPointF(x,self.height))
            painter.setPen(QColor("white"))
            painter.drawText(QPointF(x + 4,self.height - 8), str(x//24))
        
        for y in range(0, self.height, 24):
            painter.setPen(QColor(128,128,128,255))
            painter.drawLine(QPointF(0,y), QPointF(self.width,y))
            painter.setPen(QColor("white"))
            painter.drawText(QPointF(4,y + 8), str(y//24))
        
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Helvetica", 12))
        painter.drawText(QPointF(10,20), self.title)

class TypeSelector(QWidget):

    
    def __init__(self, width, height):

        super().__init__()

        self.brush_index = 0

        self.setFixedSize(QSize(width, height))

        self.layout = QHBoxLayout()
        self.left_brush_button = QPushButton(QIcon(QPixmap("gfx/left-arrow.png", "png")),"")
        self.label = QLabel(BRUSHES[self.brush_index])
        self.right_brush_button = QPushButton(QIcon(QPixmap("gfx/right-arrow.png", "png")),"")
        self.layout.addWidget(self.left_brush_button)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.right_brush_button)
        self.setLayout(self.layout)

class PropertyEditor(QWidget):

    
    def __init__(self, width, height):

        super().__init__()

        self.setFixedSize(QSize(width, height))

        self.layout = QHBoxLayout()
        self.label = QLabel("Property Editor")
        self.layout.addWidget(self.label)
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

app = QApplication(sys.argv)

window = Editor()
window.show()

app.exec()