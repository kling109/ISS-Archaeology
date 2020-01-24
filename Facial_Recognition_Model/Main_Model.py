import Astro
import pickle
import face_recognition
import os
import re
import numpy as np
import multiprocessing as mp
from multiprocessing import Process

#Just a helper method, carry on...
def getDir(filePath:str):
    if "/" not in filePath and "\\" not in filePath:
        return "./"
    regex = re.compile(r"\/")
    filePath = regex.split(filePath)
    return "/".join(filePath[:-1])+"/"
 
class Master_Model:
    """Model trained to find all astronauts. Contains methods for adding astronauts to
        model,searching a picture for astronauts, or searching all pictures in a 
        directory for any of the astronauts in the model. Must be in a directory
        with a folder for storing pickled face_recognition models. Any .dat files 
        in that directory will be added to the model.
        
        Model takes a LONG TIME to train and to search an image for faces. This will hopefully be improved soon, but for testing puposes only run on a subset of astronauts"""


    def __init__(self, train_dir:str, astro_pickle_dir:str, num_threads = 1):
        """Class constructor for Main_Model.

        PARAM: train_dir:str = directory containing pictures of all astronauts to be added to model. Picture files must follow the following naming convention: 
                <first name>_[<middle name>_]<last name>&<nationality>.jpg

            astro_pickle_dir:str = Directory in which face_recognition model objects will be flattened and saved as .dat files. Note that any .dat files in this directory will be added to model

            num_threads:int = Number of threads to be used by the model (not yet implemented)"""
        self.astro_pickle_dir = astro_pickle_dir
        self.num_threads = abs(num_threads)
        self.known_faces = self.itemizeKnown()
        self.found_faces = {}
        self.train(train_dir)


    def train(self,train_dir:str):     
        """Function adds astronaut objects to model for every image in the given directory and trains the astonaut object to recognize the face in the image. If an image in the directory already has a corresponding .dat file in astro_pickle_dir, it will be ignored.

        Param: train_dir: Directory in which all images to be trained on are stored. Images must follow this naming convention:
                <first name>_[<middle name>_]<last name>&<nationality>.jpg"""
        semaphore = mp.Semaphore(self.num_threads)
        processes = []
        lock = mp.Lock()
        for filename in os.listdir(train_dir):
            semaphore.acquire()
            lock.acquire()
            print("Training on image:", filename)
            lock.release()
            p = Process(target = self.addAstro, args = ("{0}{1}".format(train_dir,filename), semaphore,lock))
            processes.append(p)
            p.start()
        for proc in processes:
            proc.join()
            

            
    def addAstro(self,astronaut,sem:mp.Semaphore, lock:mp.Lock):
        """File adds given astronaut object or picture to model.
        
        Parameter:
        astronaut = Can by of type Astro.Astronaut or str (in which case it should be a file path). If it is of type Astro.Astronaut, astronaut will be directly added to the model. If it is a filepath, an astronaut object will be created, trained on the image, and added to the model. Filepath must follow naming conventions outlined in Master_Model.train()
            """
        if type(astronaut) == Astro.Astronaut:
            astronaut.saveData(self.astro_pickle_dir)
            self.known_faces[astronaut.filename] = astronaut.facialData
        if type(astronaut) == str:
            a = self.astroInit(astronaut)
            if(a==None):
               sem.release() 
               return
            if a.filename in self.known_faces:
                lock.acquire()
                print("\tModel has already been trained on",astronaut)
                lock.release()
                sem.release()
                return
            a.trainModel(astronaut,lock)
            if type(a.facialData) == np.ndarray:
                a.saveData(self.astro_pickle_dir)
                self.known_faces[a.filename] = a.facialData
            sem.release()

    def addAstros(self, astros:list):
        """Same behavior as addAstro, but works on a list of filepaths or astronaut objects"""
        for a in astros:
            self.addAstro(a)
    
    def astroInit(self, filepath):
        #helper method, nothing to see here...
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

    def loadAstro(self, filePath):
        #helper method, nothing to see here...
        a = self.astroInit(filePath)
        directory = getDir(filePath)
        if a == None:
            return None
        a.loadData(directory)
        return a

    def findFaces(self,img_path:str):
        """Method searches image for astronaut faces

        Parameters:
        img_path:str = path of image to search for astronaut faces.

        Returns:
        img_entry:dict = Dictionary object consisting of (a:i) pairs where a is the found astronaut, i is the index of the face attributed to the astronaut. Indicies are generated by the face_recognition library.
        """
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
        """Method searches all images in given directory for astronaut faces
        
        Parameters:
        img_dir:str = path to directory containing images to search
        
        Side-Effect: Adds entries (img: dict) to found_faces dictionary, where img is the filepath of an image and the dict is the dictionary returned from findFaces(img)

        Returns: 
        found_faces = dictionary containing entries (img:dict) as defined in the Side-Effects. Note that the returned variable is also an instance variable of the class.
        """
        for filename in os.listdir(img_dir):
            regex = re.compile(r"\.")
            print(regex.split(filename))
            if regex.split(filename)[-1] != "jpg": continue
            fullpath = img_dir+filename
            self.found_faces[filename] = self.findFaces(fullpath)
        return self.found_faces
            
    def itemizeKnown(self):
        #helper method, nothing to see here...
        known_astro = {}
        for filename in os.listdir(self.astro_pickle_dir):
            with open('{0}{1}'.format(self.astro_pickle_dir,filename),'rb') as f:
                known_astro.update(pickle.load(f))
        return known_astro

