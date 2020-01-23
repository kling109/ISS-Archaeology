import Main_Model
import os

model = Main_Model.Master_Model(r"../cropped_Astronaut_photos/",r'./pickles_bin/')
folders_list = os.walk("./ISS_Photos")
folders = [item[0] for item in folder_list]
for f in folders:
    model.findFacesDir("./ISS_Photos/" + f)
print(len(folders))
d = model.found_faces
print(d)
