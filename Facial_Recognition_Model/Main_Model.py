import Astro
import pickle
import face_recognition
import os
import re
import numpy as np

def getDir(filePath:str):
    if "/" not in filePath and "\\" not in filePath:
        return "./"
    regex = re.compile(r"\/")
    filePath = regex.split(filePath)
    return "/".join(filePath[:-1])+"/"
 
class Main_Model:

    def __init__(self, train_dir:str, astro_pickle_dir:str, num_threads = 1):
        self.astro_pickle_dir = astro_pickle_dir
        self.num_threads = abs(num_threads)
        self.known_faces = self.itemizeKnown()
        self.found_faces = {}
        self.train(train_dir)

    def train(self,train_dir:str):
        for filename in os.listdir(train_dir):
            print("Training on image:", filename)
            self.addAstro("{0}{1}".format(train_dir,filename)) 
            
    def addAstro(self,astronaut):
        if type(astronaut) == Astro.Astronaut:
            astronaut.saveData(self.astro_pickle_dir)
            self.known_faces[astronaut.filename] = astronaut.facialData
        if type(astronaut) == str:
            a = self.astroInit(astronaut)
            if(a==None):
               return
            if a.filename in self.known_faces:
                print("\tModel has already been trained on",astronaut)
                return
            a.trainModel(astronaut)
            print(type(a.facialData))
            if type(a.facialData) == np.ndarray:
                a.saveData(self.astro_pickle_dir)
                self.known_faces[a.filename] = a.facialData
        
    def astroInit(self, filepath):
        regex_noPath = re.compile(r'\/') 
        regex_names = re.compile(r"\W|_")
        filename = regex_noPath.split(filepath)[-1]
        ident = regex_names.split(filename)
        if "cropped" in ident:
            ident.remove("cropped")
        if len(ident)==5:
            fName, lName, mName, country, _ = ident    
            return Astro.Astronaut(country,fName,lName,mName)
        elif len(ident)==4:
            fName, lName, country, _ = ident
            return Astro.Astronaut(country, fName, lName)
        else:
            print("\tIncorrectly formatted file name: {}\n\tFiles must be named <first name>_<lastname>&country.jpg".format(filename))
            return None

    def addAstros(self, astros:list):
        for a in astros:
            self.addAstro(a)

    def loadAstro(self, filePath):
        a = self.astroInit(filePath)
        directory = getDir(filePath)
        if a == None:
            return None
        a.loadData(directory)
        return a

    def findFaces(self,img_path):
        img_entry = {}
        try:
            unknown_image = face_recognition.load_image_file(img_path)
            unknown_encodings = face_recognition.face_encodings(unknown_image)
        except IndexError:
            print("\tI wasn't able to locate any faces in image:",img_path)
            return None
        for filename in os.listdir(self.astro_pickle_dir):
            fullpath = self.astro_pickle_dir+filename
            print(fullpath)
            astro = self.loadAstro(fullpath)
            if astro == None:
                return None 
            found_arr = astro.checkFace(unknown_encodings)
            print(found_arr)
            if sum(found_arr) == 0 :
                continue
            else:
                img_entry[astro.filename] = []
                for i in range(len(found_arr)):
                    if found_arr[i] != 0:
                        img_entry[astro.filename].append(i)
        return img_entry
                        
    def findFacesDir(self, img_dir):
        for filename in os.listdir(img_dir):
            regex = re.compile(r"\.")
            print(regex.split(filename))
            if regex.split(filename)[-1] != "jpg": continue
            fullpath = img_dir+filename
            self.found_faces[filename] = self.findFaces(fullpath)
            
    def itemizeKnown(self):
        known_astro = {}
        for filename in os.listdir(self.astro_pickle_dir):
            with open('{0}{1}'.format(self.astro_pickle_dir,filename),'rb') as f:
                known_astro.update(pickle.load(f))
        return known_astro

