import face_recognition # https://github.com/ageitgey/face_recognition
from PIL import Image # https://pillow.readthedocs.io/en/stable/
import os, sys

def transformCoord(coordinates):
    return (coordinates[3], coordinates[0], coordinates[1], coordinates[2])

imgs = os.listdir()
for f in imgs:
    if (f.find(".jpeg") != -1):
        image = face_recognition.load_image_file(f)
        face_locations = face_recognition.face_locations(image)

        toCrop = Image.open(f).crop(transformCoord(face_locations[0]))

        toCrop.save("cropped_"+f, "JPEG")
        os.remove(f)
        print(f)
