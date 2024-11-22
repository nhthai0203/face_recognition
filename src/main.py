import cv2
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QStackedLayout, QPushButton
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Main window settings
        self.setWindowTitle("Facal Recognition Attendance System")
        self.setGeometry(250, 70, 1200, 800)
        self.setStyleSheet("background-color: lightpink;")

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Stack navigator
        self.stack_navigator = QStackedLayout()
        self.central_widget.setLayout(self.stack_navigator)

        # Camera page
        self.camera_page = CameraPage()
        self.stack_navigator.addWidget(self.camera_page)

        self.stack_navigator.setCurrentIndex(0)


        




class CameraPage(QWidget):
    def __init__(self):
        super().__init__()

        # Camera settings
        self.cam = cv2.VideoCapture(0)
        self.cam_label = QLabel(self)

        # Timer for update frame
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)

    def update_frame(self):
        ret, frame = self.cam.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            qimg = QImage(frame.data, w, h, w * ch, QImage.Format.Format_RGB888)
            qpix = QPixmap(qimg)
            self.cam_label.setPixmap(qpix)


        

    
        

        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())