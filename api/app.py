from flask import Flask, request
from flask_restful import Api, Resource
import face_recognition
import os, json, pickle
import numpy as np

# Initialize the Flask app
app = Flask(__name__)
api = Api(app)

known_face_encodings = []
student_IDs = []

# Create the resources
class FaceRecognize(Resource):
    def post(self):
        # Get the image from client
        image_file = request.files["image"]
        
        # Save the image temporarily     
        image_file.save("temp.jpg")

        # Encoding face
        image = face_recognition.load_image_file("temp.jpg")
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
        image_file.save("temp.jpg")
        
        # Encoding face
        image = face_recognition.load_image_file("temp.jpg")
        encodings = face_recognition.face_encodings(image)
        if len(encodings) == 0:
            return {"message": "No face detected"}, 400
        known_face_encodings.append(encodings[0])
        student_IDs.append(student_ID)
        return {"message": "Face registered"}, 200
    
api.add_resource(FaceRecognize, "/face_recognize") 
api.add_resource(RegisterFace, "/register_face/<string:student_ID>")

def save_known_face_encodings():
    with open("api/known_face_encodings.json", "w") as f:
        data = dict(zip(student_IDs, [encoding.tolist() for encoding in known_face_encodings]))
        json.dump(data, f)
# atexit.register(save_known_face_encodings)

if __name__ == "__main__":
    if os.path.getsize("api/known_face_encodings.json") > 0:
        with open("api/known_face_encodings.json", "r") as f:
            data = json.load(f)
            for key, value in data.items():
                known_face_encodings.append(np.array(value))
                student_IDs.append(key)
    try:
        app.run(debug=True)
    finally:
        save_known_face_encodings()
        if os.path.exists("temp.jpg"):
            os.remove("temp.jpg")