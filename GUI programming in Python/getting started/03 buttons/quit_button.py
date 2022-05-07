import sys

from PyQt6.QtWidgets import (
    QApplication, QDialog, QMainWindow, QPushButton,
    QLabel, QDialogButtonBox, QVBoxLayout, QWidget
)

class MessageDialog(QDialog):


    def __init__(self):

        super().__init__()

        self.setWindowTitle("response")

        button = QDialogButtonBox.StandardButton.Ok

        self.buttonBox = QDialogButtonBox(button)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        message = QLabel("Thanks for clicking the button")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

class MainWindow(QMainWindow):


    def __init__(self):

        super().__init__()

        self.setWindowTitle("My App")

        button1 = QPushButton("Click Me!")
        button1.clicked.connect(self.button1_clicked)

        button2 = QPushButton("Quit")
        button2.clicked.connect(self.button2_clicked)

        layout = QVBoxLayout()
        layout.addWidget(button1)
        layout.addWidget(button2)

        widget = QWidget()
        widget.setLayout(layout)
        
        self.setCentralWidget(widget)

    def button1_clicked(self):

        dlg = MessageDialog()
        if dlg.exec():
            print("Button was clicked.")

    def button2_clicked(self):

        self.destroy()

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()