import sys

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QHBoxLayout,
    QLabel, QVBoxLayout, QWidget, QLineEdit
)

class MainWindow(QMainWindow):


    def __init__(self):

        super().__init__()

        self.setWindowTitle("My App")

        #widgets
        km_label = QLabel("Distance (km): ")
        self.km_input_field = QLineEdit()
        km_container = QWidget()
        self.miles_label = QLabel("Distance (miles): ")
        convert_button = QPushButton("Convert to miles")
        exit_button = QPushButton("Quit")
        button_container = QWidget()
        app_container = QWidget()

        #connect buttons to actions
        convert_button.clicked.connect(self.convert)
        exit_button.clicked.connect(self.exit)

        #layouts
        km_row = QHBoxLayout()
        button_row = QHBoxLayout()
        app_column = QVBoxLayout()

        #add widgets to layouts
        km_row.addWidget(km_label)
        km_row.addWidget(self.km_input_field)
        km_container.setLayout(km_row)
        button_row.addWidget(convert_button)
        button_row.addWidget(exit_button)
        button_container.setLayout(button_row)
        app_column.addWidget(km_container)
        app_column.addWidget(self.miles_label)
        app_column.addWidget(button_container)
        app_container.setLayout(app_column)
        
        self.setCentralWidget(app_container)

    def convert(self):

        kilometres = float(self.km_input_field.text())
        miles = kilometres * 0.621371
        self.miles_label.setText(f"Distance (miles): {miles}")

    def exit(self):

        self.close()

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()