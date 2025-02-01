import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget

class MainWindow(QMainWindow):


    def __init__(self):
    
        super().__init__()

        self.setWindowTitle("My App")

        label1 = QLabel()
        label1.setText("Hello, world!")
        label2 = QLabel()
        label2.setText("This is my GUI program!")

        layout = QVBoxLayout()
        layout.addWidget(label1)
        layout.addWidget(label2)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()