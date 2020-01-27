# -*- coding: utf-8 -*-

import cv2

CONFIDENCE_THRESHOLD = 0.1


def detect_faces(image):
    model_file = "models/opencv_face_detector_uint8.pb"
    config_file = "models/opencv_face_detector.pbtxt"
    net = cv2.dnn.readNetFromTensorflow(model_file, config_file)
    height, width, _ = image.shape

    # https://github.com/opencv/opencv/tree/master/samples/dnn
    blob = cv2.dnn.blobFromImage(image, size=(300, 300), mean=[104, 177, 123])

    net.setInput(blob)
    detections = net.forward()

    faces = []

    for detection in detections[0, 0]:
        _, _, confidence, x1, y1, x2, y2 = detection

        if confidence > CONFIDENCE_THRESHOLD:
            faces.append([confidence, max(int(x1 * width), 0), max(int(y1 * height), 0), int(x2 * width), int(y2 * height)])

    return faces


def detect_eyes(image, x_offset, y_offset):
    eye_cascade = cv2.CascadeClassifier("models/haarcascade_eye.xml")
    detection = eye_cascade.detectMultiScale(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))

    eyes = []

    for (x, y, w, h) in detection:
        eyes.append([x + x_offset, y + y_offset, x + x_offset + w, y + y_offset + h])

    return eyes


# Testing this with an image.
if __name__ == "__main__":
    image = cv2.imread("images/testimg.jpg")
    faces = detect_faces(image)

    for face in faces:
        cv2.rectangle(image, (face[1], face[2]), (face[3], face[4]), (0, 255, 0), 2, 8)
        cv2.putText(image, str(round(face[0], 2)), (face[1] + 5, face[2] + 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        eye_roi = image[face[2]:face[4], face[1]:face[3]]
        # cv2.imwrite("images/eyeroi.jpg", eye_roi)
        # eyes = detect_eyes(eye_roi, face[1], face[2])

        # for eye in eyes:
        #     cv2.rectangle(image, (eye[0], eye[1]), (eye[2], eye[3]), (0, 127, 255), 2, 8)
        #     cv2.circle(image, (int(eye[2] - ((eye[2] - eye[0]) / 2)), int(eye[3] - ((eye[3] - eye[1]) / 2))), 1, (255, 0, 0), 2, 1)


    cv2.imwrite("images/resultimg.jpg", image)
