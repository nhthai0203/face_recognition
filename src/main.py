import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import cv2, sys, os, requests
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QStackedLayout, QPushButton, QVBoxLayout, QHBoxLayout, QDialog, QLineEdit, QMessageBox
from PyQt6.QtGui import QImage, QPixmap, QAction
from PyQt6.QtCore import QTimer

# Constants
API_KEY = "http://127.0.0.1:5000/"
RAW_PHOTO_PATH = "src/temp/raw_photo.jpg"
FACE_DETECTED_PHOTO_PATH = "src/temp/face_detected_photo.jpg"
TEMP_ATTENDANCE_PATH = "src/temp/temp_attendance.csv"
ATTENDANCE_PATH = "src/attendance.csv"

class MainWindow(QMainWindow):
    temp_data = {}
    temp_attendance = []
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
            QMenuBar {
                background-color: lightpink
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
        self.create_menu_bar()

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

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        settings = menu_bar.addMenu("Settings")

        open_attendance_list_action = QAction("Open attendance list", self)
        open_attendance_list_action.triggered.connect(self.open_attendance_list)
        settings.addAction(open_attendance_list_action)

    def open_attendance_list(self):
        pass

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
        response = requests.post(API_KEY + "face_recognize", files={"image": open(RAW_PHOTO_PATH, "rb")})
        
        if response.status_code != 400:
            top, right, bottom, left = response.json()["face_location"]
            color = (0, 255, 0) if response.status_code == 200 else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left - 1, bottom + 35), (right + 1, bottom), color, cv2.FILLED)
            cv2.putText(frame, response.json()["message"], (left + 6, bottom + 27), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)
            cv2.imwrite(FACE_DETECTED_PHOTO_PATH, frame)

        if response.status_code == 200:
            MainWindow.change_page(1, "Face recognized: " + response.json()["message"])
            now = datetime.now()
            MainWindow.temp_data = {"student": response.json()["message"], "time": f"{now:%Y-%m-%d %H:%M:%S}"}
        elif response.status_code == 404:
            MainWindow.change_page(2, "Face not recognized: " + response.json()["message"])
        else:
            MainWindow.status = "Error: " + response.json()["message"]

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
        if "student" in MainWindow.temp_data and "time" in MainWindow.temp_data:
            if MainWindow.temp_data["student"] in MainWindow.temp_attendance:
                message_box = QMessageBox.information(None, "Information", "Your attendance has already marked")
                return
            
            with open(ATTENDANCE_PATH, "a") as f:
                f.write(f'{MainWindow.temp_data["student"]}, {MainWindow.temp_data["time"]}\n')
                MainWindow.temp_attendance.append(MainWindow.temp_data["student"])
                message_box = QMessageBox.information(None, "Information", "Mark attendance successfully")

            with open(TEMP_ATTENDANCE_PATH, "a") as f:
                f.write(f'{MainWindow.temp_data["student"]}, {MainWindow.temp_data["time"]}\n')

    def retake_photo(self):
        MainWindow.change_page(0, "Take photo again")
        MainWindow.temp_data = {}

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
        response = requests.post(API_KEY + "register_face/" + student_id, files={"image": open(RAW_PHOTO_PATH, "rb")})
        self.close()
        MainWindow.change_page(0, "Take photo again to recognize")

def remove_paths(*paths):
    for path in paths:
        if os.path.exists(path):
            os.remove(path)

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    finally:
        if len(window.temp_attendance) > 0:
            with open(ATTENDANCE_PATH, "a") as f:
                f.write(f"(Count: {len(window.temp_attendance)})" + "\n")
                f.write("\n")
        window.camera_page.cam.release()
        remove_paths(RAW_PHOTO_PATH, FACE_DETECTED_PHOTO_PATH, TEMP_ATTENDANCE_PATH)

        # if os.path.exists(RAW_PHOTO_PATH):
        #     os.remove(RAW_PHOTO_PATH)
        # if os.path.exists(FACE_DETECTED_PHOTO_PATH):
        #     os.remove(FACE_DETECTED_PHOTO_PATH)
        # if os.path.exists(TEMP_ATTENDANCE_PATH):
        #     os.remove(TEMP_ATTENDANCE_PATH)