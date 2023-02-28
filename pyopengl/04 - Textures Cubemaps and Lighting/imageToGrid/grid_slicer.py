import sys

from PyQt6.QtGui import QAction
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (
  QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,
  QPushButton, QFileDialog
)

import gl_widgets
import grid

class Parameter(QWidget):


  def __init__(self, title, start_value):

    super().__init__()
    self.layout = QHBoxLayout()
    self.label = QLabel(title)
    self.field = QLineEdit(str(start_value))
    self.layout.addWidget(self.label)
    self.layout.addWidget(self.field)
    self.setLayout(self.layout)
  
  def get_value(self):

    return self.field.text()

class Window(QMainWindow):


  def __init__(self):

    super().__init__()

    self.setWindowTitle("Image Editor")

    self.createMenu()

    self.create_widgets()

  def create_widgets(self):

    self.image_frame = gl_widgets.ImageFrame(800,600)

    self.parameter_layout = QVBoxLayout()
    self.row_parameter = Parameter("Rows",grid.grid.rows)
    self.col_parameter = Parameter("Columns",grid.grid.cols)
    self.update_btn = QPushButton("Update Grid")
    self.update_btn.pressed.connect(self.update_grid)
    self.parameter_layout.addWidget(self.row_parameter)
    self.parameter_layout.addWidget(self.col_parameter)
    self.parameter_layout.addWidget(self.update_btn)

    self.parameter_frame = QWidget()
    self.parameter_frame.setFixedSize(QSize(200,600))
    self.parameter_frame.setLayout(self.parameter_layout)
    
    self.main_layout = QHBoxLayout()
    self.main_layout.addWidget(self.image_frame)
    self.main_layout.addWidget(self.parameter_frame)
    self.main_widget = QWidget()
    self.main_widget.setLayout(self.main_layout)

    self.setCentralWidget(self.main_widget)
  
  def createMenu(self):

    self.menu_bar = self.menuBar()
    self.file_menu = self.menu_bar.addMenu("File")

    self.new_button = QAction("New Blank", self)
    self.new_button.triggered.connect(self.newImage)
    self.file_menu.addAction(self.new_button)

    self.export_button = QAction("Export", self)
    self.export_button.triggered.connect(self.exportImages)
    self.file_menu.addAction(self.export_button)

    self.import_button = QAction("Import", self)
    self.import_button.triggered.connect(self.importImages)
    self.file_menu.addAction(self.import_button)
  
  def update_grid(self):

    rows = int(self.row_parameter.get_value())
    cols = int(self.col_parameter.get_value())
    grid.grid.update(800, 600, rows, cols)
    self.image_frame.repaint()
  
  def newImage(self):

    self.image_frame.unload_image()
    self.image_frame.repaint()
  
  def exportImages(self):
    
    self.image_frame.export_images()
  
  def importImages(self):
    
    filename = QFileDialog.getOpenFileName(self)
    if len(filename[0]) > 0:
        self.image_frame.load_image(filename[0])
    self.image_frame.repaint()

app = QApplication(sys.argv)
window = Window()
window.show()
app.exec()