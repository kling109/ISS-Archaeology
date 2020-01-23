import Main_Model

model = Main_Model.Master_Model(r"../cropped_Astronaut_photos/",r'./pickles_bin/')
model.findFacesDir("../Test/")
print("5")
d = model.found_faces
print(d)