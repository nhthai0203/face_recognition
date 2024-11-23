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
        encodings = face_recognition.face_encodings(image)
        if len(encodings) == 0:
            return {"message": "No face detected"}, 422
        compare_list = face_recognition.compare_faces(known_face_encodings, encodings[0])
        if True in compare_list:
            return {"message": student_IDs[compare_list.index(True)]}, 200
        return {"message": "Unknown face"}, 404

class RegisterFace(Resource):
    def post(self, student_ID):
        # Get the image and student ID from client
        image_file = request.files["image"]
        
        # Save the image temporarily
        image_file.save(TEMP_PATH)
        
        # Encoding face
        image = face_recognition.load_image_file(TEMP_PATH)
        encodings = face_recognition.face_encodings(image)
        if len(encodings) == 0:
            return {"message": "No face detected"}, 400
        known_face_encodings.append(encodings[0])
        student_IDs.append(student_ID)
        save_encoding(student_ID, encodings[0].tolist())
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

if __name__ == "__main__":
    try:
        load_data()
        app.run(debug=True)
    finally:
        if os.path.exists(TEMP_PATH):
            os.remove(TEMP_PATH)