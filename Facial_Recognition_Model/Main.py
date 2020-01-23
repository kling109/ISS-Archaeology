import Main_Model

model = Main_Model.Main_Model(r"../cropped_Astronaut_photos/",r'./pickles_bin/')
model.findFacesDir("../Test/")
print("5")
d = model.found_faces
print(d)