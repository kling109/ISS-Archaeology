import Main_Model
import os

if __name__ == '__main__':
    model = Main_Model.Master_Model(r"../cropped_Astronaut_photos/",r'./pickles_bin/',5)
    model.findFacesDir("../Test/")
    d = model.found_faces
    for k,v in d.items():
        print(k,"matched with:",v)
