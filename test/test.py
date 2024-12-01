import os, face_recognition, json

ENCODINGS_PATH = "test/test_encodings"
IMAGES_PATH = "test/test_images"

for index, path in enumerate(os.listdir(IMAGES_PATH)):
    image = face_recognition.load_image_file(IMAGES_PATH + "/" + path)
    encoding = face_recognition.face_encodings(image)[0]
    with open(f"{ENCODINGS_PATH}/face{index + 1}.json", "w") as f:
        json.dump(encoding.tolist(), f)