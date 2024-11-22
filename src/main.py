import tkinter as tk
from PIL import Image, ImageTk
import cv2
import util2
import face_recognition
import sys

class App:
    def __init__(self):
        self.faces_exist = False
        self.image_list = {}
        # main window
        self.main_window = tk.Tk()
        self.main_window.geometry("1100x600")
        # position of take photo button
        self.take_photo_button = util2.get_button(self.main_window, 'Take photo', 'lightblue2', self.take_photo)
        self.take_photo_button.place(x=750, y=300)
        # position of the webcam label
        self.webcam_label = util2.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=10, width=700, height=500)
        self.cap = cv2.VideoCapture(0)
        self.show_webcam()
    
    def show_webcam(self):
        ret, frame = self.cap.read()  # capture frame


        if ret:
            # convert frame to a format suitable for Tkinter and face_location
            cv2_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # BGR to RGB
            largest_face_area = 0
            largest_face = None

            face_locations = face_recognition.face_locations(cv2_image, model="hog")
            if face_locations:
            # Loop through each face
                for top,right,bottom,left in face_locations:
                    face_area = (right - left) * (bottom - top)

                    # Update largest face if this has a bigger area
                    if face_area > largest_face_area:
                        largest_face_area = face_area
                        largest_face = (top, right, bottom, left)

                # If a largest face is found, draw rectangle and potentially capture it
                if largest_face:
                    top, right, bottom, left = largest_face
                    cv2.rectangle(cv2_image, (left, top), (right, bottom), (0, 255, 0), 2)

                    # add images to image_list
                    self.image_list["cut_face"] = cv2_image[top:bottom,left:right]
                    self.image_list["full_image"] = cv2_image
                    self.faces_exist = True
            else:
                self.faces_exist = False
            # cv2_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # BGR to RGB

            img = Image.fromarray(cv2_image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.webcam_label.config(image=imgtk)
            self.webcam_label.image = imgtk  # keep a reference

        self.main_window.after(1, self.show_webcam)  # call this method again after 10ms

        
    
    # save images form image_list if face detected
    def take_photo(self):
        if self.faces_exist:
            self.image_list["full_image"] = cv2.cvtColor(self.image_list["full_image"], cv2.COLOR_BGR2RGB)
            cv2.imwrite('./.cf.jpg', self.image_list["cut_face"])
            cv2.imwrite('./.fi.jpg', self.image_list["full_image"])

    def start(self):
        self.main_window.mainloop()

if __name__ == "__main__":
    app = App()
    app.start()