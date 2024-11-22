import cv2
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QStackedLayout, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Main window settings
        self.setWindowTitle("Facal Recognition Attendance System")
        self.setGeometry(400, 100, 1000, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: lightpink;
            }
            QPushButton {
                background-color: lightpink;
                color: purple;
                border: 2px solid purple;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: purple;
                color: lightpink;
            }
            QPushButton:pressed {
                background-color: violet;
                color: mangenta;
            }
            """)
    

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Stack navigator
        self.stack_navigator = QStackedLayout()
        self.central_widget.setLayout(self.stack_navigator)

        # Pages
        self.camera_page = CameraPage(self.stack_navigator)
        self.attendance_page = AttendancePage(self.stack_navigator)

        # Set current index
        self.stack_navigator.setCurrentIndex(0)



class CameraPage(QWidget):
    def __init__(self, stack_navigator):
        super().__init__()
        self.stack_navigator = stack_navigator
        self.stack_navigator.addWidget(self)

        # Camera settings
        self.cam = cv2.VideoCapture(0)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Layout settings
        self.hbox = QHBoxLayout()
        self.setLayout(self.hbox)    

        self.cam_label = QLabel()
        self.cam_label.setFixedSize(640, 480)
        self.hbox.addWidget(self.cam_label)

        self.take_photo_btn = QPushButton("Take Photo")
        self.take_photo_btn.setFixedSize(150, 60)
        self.take_photo_btn.clicked.connect(self.take_photo)
        self.hbox.addWidget(self.take_photo_btn)

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
            qpix = QPixmap.fromImage(qimg)
            self.cam_label.setPixmap(qpix)

    def take_photo(self):
        cv2.imwrite("photo.jpg", self.cam.read()[1])
        self.stack_navigator.setCurrentIndex(1)


class AttendancePage(QWidget):
    def __init__(self, stack_navigator):
        super().__init__()
        self.stack_navigator = stack_navigator
        self.stack_navigator.addWidget(self)

        # Layout settings
        self.vbox = QVBoxLayout()
        self.hbox = QHBoxLayout()
        self.setLayout(self.hbox)

        self.image_label = QLabel()
        self.image_label.setFixedSize(640, 480)
        self.hbox.addWidget(self.image_label)
        self.hbox.addLayout(self.vbox)

        self.mark_attendance_btn = QPushButton("Mark Attendance")
        self.mark_attendance_btn.setFixedSize(150, 60)
        self.mark_attendance_btn.clicked.connect(self.mark_attendance)
        self.vbox.addWidget(self.mark_attendance_btn)

        self.retake_photo_btn = QPushButton("Retake Photo")
        self.retake_photo_btn.setFixedSize(150, 60)
        self.retake_photo_btn.clicked.connect(self.retake_photo)
        self.vbox.addWidget(self.retake_photo_btn)

        self.timer = QTimer()
        self.timer.timeout.connect(self.show_photo)
        self.timer.start(10)



    def show_photo(self):
        self.image_label.setPixmap(QPixmap("photo.jpg"))

    def mark_attendance(self):
        pass

    def retake_photo(self):
        self.stack_navigator.setCurrentIndex(0)



class RegisterPage(QWidget):
    def __init__(self):
        super().__init__()

    def register(self):
        pass

    def retake_photo(self):
        pass



class InputPage(QWidget):
    def __init__(self):
        super().__init__()

    def input(self):
        pass

    def retake_photo(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())