import cv2

# Load the profile face Haar cascade
profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')

# Read the image
image = cv2.imread("m.jpg")
# image = cv2.resize(image,(640, 640))
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Detect profile faces in the image
profile_faces = profile_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=1, minSize=(30, 30))
print(profile_faces)

# Draw rectangles around detected faces
for (x, y, w, h) in profile_faces:
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

# Show the image with detected profile faces
cv2.imshow("Profile Faces Detected", image)
cv2.waitKey(0)
cv2.destroyAllWindows()