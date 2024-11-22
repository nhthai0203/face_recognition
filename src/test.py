import tkinter as tk
from PIL import Image, ImageTk
import cv2
import util2
import face_recognition

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
            # Convert frame from BGR to RGB (for Tkinter compatibility)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            largest_face_area = 0
            largest_face = None

            # Use face_recognition to find faces
            face_locations = face_recognition.face_locations(rgb_frame)
            if face_locations:
                # Loop through each face and find the largest one
                for top, right, bottom, left in face_locations:
                    face_area = (right - left) * (bottom - top)

                    # Update the largest face if this one is bigger
                    if face_area > largest_face_area:
                        largest_face_area = face_area
                        largest_face = (top, right, bottom, left)

                # If a face is found, draw rectangle and capture face image
                if largest_face:
                    top, right, bottom, left = largest_face
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    
                    # Add images to image_list
                    self.image_list["cut_face"] = frame[top:bottom, left:right]
                    self.image_list["full_image"] = frame
                    self.faces_exist = True
            else:
                self.faces_exist = False

            # Convert frame to RGB for Tkinter
            img = Image.fromarray(rgb_frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.webcam_label.config(image=imgtk)
            self.webcam_label.image = imgtk  # keep a reference

        # Call this method again after a short delay
        self.main_window.after(1, self.show_webcam)

    def take_photo(self):
        if self.faces_exist:
            # Save the images when a face is detected
            cv2.imwrite('./.cf.jpg', self.image_list["cut_face"])
            cv2.imwrite('./.fi.jpg', self.image_list["full_image"])
            print("Images saved successfully!")
        else:
            print("No face detected, try again!")

    def start(self):
        self.main_window.mainloop()

if __name__ == "__main__":
    app = App()
    app.start()
