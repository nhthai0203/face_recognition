import face_recognition

class FaceRecognize(Resource):
    def post(self):
        # Get the image from the request
        image = request.files['image']

        # Save the image to a temporary file
        image_path = '/tmp/' + image.filename
        image.save(image_path)

        # Load the image
        image = cv2.imread(image_path)

        # Detect faces in the image
        face_locations = face_recognition.face_locations(image)

        # Return the face locations
        return {'face_locations': face_locations}