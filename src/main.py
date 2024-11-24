import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import cv2
import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QStackedLayout, QPushButton, QVBoxLayout, QHBoxLayout, QDialog, QLineEdit
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer
import requests

API_KEY = "http://127.0.0.1:5000/"
RAW_PHOTO_PATH = "src/raw_photo.jpg"
FACE_DETECTED_PHOTO_PATH = "src/face_detected_photo.jpg"

class MainWindow(QMainWindow):
    status = "Take photo to recognize"
    stack_navigator = QStackedLayout()

    def __init__(self):
        super().__init__()
        
        # Main window settings
        self.setWindowTitle("Facal Recognition Attendance System")
        self.setGeometry(400, 100, 1000, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: lightpink;
            }
            QStatusBar {
                background-color: purple;
                color: lightpink;
            }
            QLabel {
                border: 2px solid purple;
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
        self.central_widget.setLayout(self.stack_navigator)

        # Pages
        self.camera_page = CameraPage()
        self.stack_navigator.addWidget(self.camera_page)
        self.attendance_page = AttendancePage()
        self.stack_navigator.addWidget(self.attendance_page)
        self.register_page = RegisterPage()
        self.stack_navigator.addWidget(self.register_page)

        # Set current index
        self.stack_navigator.setCurrentIndex(0)

        # Timer for show status bar
        self.timer = QTimer()
        self.timer.timeout.connect(self.show_status_bar)
        self.timer.start(10)

    def show_status_bar(self):
        self.statusBar().showMessage(self.status)

    @classmethod
    def change_page(cls, index, status):
        cls.stack_navigator.setCurrentIndex(index)
        cls.status = status

class CameraPage(QWidget):
    def __init__(self):
        super().__init__()

        # Camera settings
        self.cam = cv2.VideoCapture(0)
        if not self.cam.isOpened():
            print("Error: Camera is not opened")
            sys.exit()
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
        ret, frame = self.cam.read()
        if not ret:
            return
        cv2.imwrite(RAW_PHOTO_PATH, frame)
        respone = requests.post(API_KEY + "face_recognize", files={"image": open(RAW_PHOTO_PATH, "rb")})
        if respone.status_code != 400:
            top, right, bottom, left = respone.json()["face_location"]
            color = (0, 255, 0) if respone.status_code == 200 else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left - 1, bottom + 35), (right + 1, bottom), color, cv2.FILLED)
            cv2.putText(frame, respone.json()["message"], (left + 6, bottom + 27), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)
            cv2.imwrite(FACE_DETECTED_PHOTO_PATH, frame)
        if respone.status_code == 200:
            MainWindow.change_page(1, respone.json()["message"])
        elif respone.status_code == 404:
            MainWindow.change_page(2, respone.json()["message"])

class AttendancePage(QWidget):
    def __init__(self):
        super().__init__()

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
        self.image_label.setPixmap(QPixmap(FACE_DETECTED_PHOTO_PATH))

    def mark_attendance(self):
        pass

    def retake_photo(self):
        MainWindow.change_page(0, "Take photo again")

class RegisterPage(QWidget):
    def __init__(self):
        super().__init__()

        # Layout settings
        self.vbox = QVBoxLayout()
        self.hbox = QHBoxLayout()
        self.setLayout(self.hbox)

        self.image_label = QLabel()
        self.image_label.setFixedSize(640, 480)
        self.hbox.addWidget(self.image_label)
        self.hbox.addLayout(self.vbox)

        self.register_btn = QPushButton("Register")
        self.register_btn.setFixedSize(150, 60)
        self.register_btn.clicked.connect(self.register)
        self.vbox.addWidget(self.register_btn)

        self.retake_photo_btn = QPushButton("Retake Photo")
        self.retake_photo_btn.setFixedSize(150, 60)
        self.retake_photo_btn.clicked.connect(self.retake_photo)
        self.vbox.addWidget(self.retake_photo_btn)

        self.timer = QTimer()
        self.timer.timeout.connect(self.show_photo)
        self.timer.start(10)

    def show_photo(self):
        self.image_label.setPixmap(QPixmap(FACE_DETECTED_PHOTO_PATH))

    def register(self):
        input_dialog = InputDialog()
        input_dialog.exec()

    def retake_photo(self):
        MainWindow.change_page(0, "Take photo again")

class InputDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Input Student ID")
        self.setGeometry(600, 300, 400, 200)
        self.setStyleSheet("""
            QDialog {
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
            QLineEdit {
                background-color: lightpink;
                color: purple;
                border: 2px solid purple;
                border-radius: 5px;
            }
            QLineEdit:hover {
                background-color: purple;
                color: lightpink;
            }
            QLineEdit:pressed {
                background-color: violet;
                color: mangenta;
            }
            """)

        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)

        self.student_id_input = QLineEdit()
        self.student_id_input.setPlaceholderText("Student ID")
        self.vbox.addWidget(self.student_id_input)

        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.register)
        self.vbox.addWidget(self.register_btn)

    def register(self):
        student_id = self.student_id_input.text()
        respone = requests.post(API_KEY + "register_face/" + student_id, files={"image": open(RAW_PHOTO_PATH, "rb")})
        self.close()
        MainWindow.change_page(0, "Take photo again to recognize")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    try:
        sys.exit(app.exec())
    finally:
        window.camera_page.cam.release()
        if os.path.exists(RAW_PHOTO_PATH):
            os.remove(RAW_PHOTO_PATH)
        if os.path.exists(FACE_DETECTED_PHOTO_PATH):
            os.remove(FACE_DETECTED_PHOTO_PATH)