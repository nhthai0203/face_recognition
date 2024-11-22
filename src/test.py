import face_recognition


image_path = '.\\known/2345345.jpg'
image = face_recognition.load_image_file(image_path)
face_encoding = face_recognition.face_encodings(image, model='cnn')[0]
encoding_path = '.\\known/2345345.txt'
with open(encoding_path, 'w') as f:
    for i in face_encoding:
        f.write(str(i) + '\n')