import face_recognition
from flask_restful import Resource
from flask import request

class FaceRecognize(Resource):
    def get(self):
        