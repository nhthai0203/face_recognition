from flask import Flask, request
from flask_restful import Api, Resource
import face_recognition
import os, json, pickle
import numpy as np

# Initialize the Flask app
app = Flask(__name__)
api = Api(app)

DATA_PATH = "api/data/"
TEMP_PATH = "api/temp.jpg"
known_face_encodings = []
student_IDs = []

# Create the resources
class FaceRecognize(Resource):
    def post(self):
        # Get the image from client
        image_file = request.files["image"]

        # Save the image temporarily     
        image_file.save(TEMP_PATH)

        # Encoding face
        image = face_recognition.load_image_file(TEMP_PATH)
        face_location = encoding_face(image)
        if not face_location:
            return {"message": "No face detected"}, 400
        encoding, location = face_location
        compare_list = face_recognition.compare_faces(known_face_encodings, encoding, tolerance = 0.4)
        if True in compare_list:
            return {"message": student_IDs[compare_list.index(True)], "face_location": location}, 200
        return {"message": "Unknown face", "face_location": location}, 404

class RegisterFace(Resource):
    def post(self, student_ID):
        # Get the image and student ID from client
        image_file = request.files["image"]
        
        # Save the image temporarily
        image_file.save(TEMP_PATH)
        
        # Encoding face
        image = face_recognition.load_image_file(TEMP_PATH)
        face_location = encoding_face(image)
        if not face_location:
            return {"message": "No face detected"}, 400
        encoding, _ = face_location

        known_face_encodings.append(encoding)
        student_IDs.append(student_ID)
        save_encoding(student_ID, encoding.tolist())
        return {"message": "Face registered"}, 200
    
api.add_resource(FaceRecognize, "/face_recognize") 
api.add_resource(RegisterFace, "/register_face/<string:student_ID>")

def load_data():
    for file in os.listdir(DATA_PATH):
        with open(DATA_PATH + file, "r") as f:
            encoding = json.load(f)
            known_face_encodings.append(np.array(encoding))
            student_IDs.append(file.split(".")[0])

def save_encoding(student_ID, encoding):
    with open(DATA_PATH + student_ID + ".json", "w") as f:
        json.dump(encoding, f)

def encoding_face(image):
    face_locations = face_recognition.face_locations(image)
    if len(face_locations) == 0:
        return None
    biggest_face = None
    biggest_area = 0
    for top, right, bottom, left in face_locations:
        area = (bottom - top) * (right - left)
        if area > biggest_area:
            biggest_area = area
            biggest_face = (top, right, bottom, left) 
            cut_face = image[top:bottom, left:right]
    face_encodings = face_recognition.face_encodings(cut_face)
    if len(face_encodings) == 0:
        return None
    return face_encodings[0], biggest_face

if __name__ == "__main__":
    try:
        load_data()
        app.run(debug=True)
    finally:
        if os.path.exists(TEMP_PATH):
            os.remove(TEMP_PATH)