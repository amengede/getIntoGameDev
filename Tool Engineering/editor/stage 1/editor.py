from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
)
from PyQt6.QtGui import (
    QAction, QPainter, QColor
)
from PyQt6.QtCore import (
    QSize
)
import sys

class Editor(QMainWindow):


    def __init__(self):

        super().__init__()

        self.setWindowTitle("Level Editor")

        self.createMenu()

        self.MakeWidgetsAndLayouts()
    
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

        print("make new map")
    
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
        self.map_view = MapView(width=800, height=600)
        self.type_selector = TypeSelector(width = 200, height = 50)
        self.property_editor = PropertyEditor(width = 200, height = 400)
        self.map_controller = MapController(width = 150, height = 150)

        #define layouts
        self.left_layout.addWidget(self.map_view)

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

class MapView(QWidget):

    
    def __init__(self, width, height):

        super().__init__()

        self.setFixedSize(QSize(width, height))
    
    def paintEvent(self, event):
        
        rect = event.rect()
        painter = QPainter(self)
        painter.fillRect(rect, QColor("black"))

class TypeSelector(QWidget):

    
    def __init__(self, width, height):

        super().__init__()

        self.setFixedSize(QSize(width, height))

        self.layout = QHBoxLayout()
        self.label = QLabel("Brush Selector")
        self.layout.addWidget(self.label)
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

        self.layout = QHBoxLayout()
        self.label = QLabel("Map Controller")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

app = QApplication(sys.argv)

window = Editor()
window.show()

app.exec()