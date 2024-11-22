import cv2
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Facal Recognition Attendance System")
        self.setGeometry(250, 70, 1200, 800)
        self.initUI()

    def initUI(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())