import sys

from PyQt6.QtWidgets import (
    QApplication, QDialog, QMainWindow, QPushButton,
    QLabel, QDialogButtonBox, QVBoxLayout
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

        button = QPushButton("Click Me!")
        button.clicked.connect(self.button_clicked)
        
        self.setCentralWidget(button)

    def button_clicked(self):

        dialog = MessageDialog()
        if dialog.exec():
            print("Button was clicked.")

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()