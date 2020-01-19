import os

for filename in os.listdir("./cropped_Astronaut_photos"):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        if filename[8:] not in os.listdir("./ISS_Astronaut_photos"):
            print(filename)
