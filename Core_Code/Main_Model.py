'''
@author:    Daniel Briseno
@editor:    Matt Raymond
'''

import Astro
import pickle
import face_recognition
import os
import shutil
import re
import numpy as np
import multiprocessing as mp
from multiprocessing import Process

# Whether images should be cached in a folder or not
# Prevents image from being processed again
cache_img = True
err_log = []

'''
DESC:   Gets the directory containing a file

INPUT:  A string filepath as `filePath`

OUTPUT: The directory containing the given object, represented as a string
'''
def getDir(filePath:str):
    if "/" not in filePath and "\\" not in filePath:
        return "./"
    regex = re.compile(r"\/")
    filePath = regex.split(filePath)
    return "/".join(filePath[:-1])+"/"


'''
DESC:   Returns the paritally/qualified version of a filepath

INPUT:  A string filepath as `filepath`

OUTPUT: A filepath
'''
def getFileName(filePath:str):
    if "/" not in filePath and "\\" not in filePath:
        return filePath
    regex = re.compile(r"\/")
    filePath = regex.split(filePath)
    return filePath[-1]

'''
DESC:   Creates a directory if it is missing

INPUT:  A string as the path of the directory as `fileDir`

OUTPUT: None
'''
def prepDir(fileDir:str):
    if fileDir[-1] == "/" or fileDir[-1] =="\\":
        fileDir = fileDir[:-1]
    if not os.path.isdir(fileDir):
        os.makedirs(fileDir)

'''
DESC:   Saves a pickle object to a .dat file

INPUT:  A string `directory` as the file location to save to, a string
        `file_name` as the name use for the new .dat file, and a pickle object
        `pickle_obj` as the information to be pickled

OUTPUT: None
'''
def makePickle(directory:str, file_name:str, pickle_obj):
    regex = re.compile(r"\.")
    file_name_no_extension = regex.split(file_name)[0]
    prepDir(directory)
    with open("{0}{1}.dat".format(directory,file_name_no_extension),"wb") as f:
        pickle.dump(pickle_obj,f)

'''
DESC:   Prints the error message from the error log

INPUT:  A string `msg` that holds a message to be printed along with the
        errors

OUTPUT: None
'''
def printErr(msg:str):
    if len(err_log) == 0 : return
    print(msg)
    while len(err_log) != 0:
        print("\t{}".format(err_log.pop()))


'''
Model trained to find all astronauts. Contains methods for adding astronauts to
model,searching a picture for astronauts, or searching all pictures in a
directory for any of the astronauts in the model. Must be in a directory
with a folder for storing pickled face_recognition models. Any .dat files
in that directory will be added to the model.
'''
class Master_Model:

    '''
    Class constructor for Main_Model.

    PARAM:
        train_dir:str = directory containing pictures of all astronauts to
        be added to model. Picture files must follow the following naming
        convention:
            <first name>_[<middle name>_]<last name>&<nationality>.jpg

        astro_pickle_dir:str = Directory in which face_recognition model objects
        will be flattened and saved as .dat files. Note that any .dat files in
        this directory will be added to model

        num_threads:int = Number of threads to be used by the model
    '''
    def __init__(self, train_dir:str, astro_pickle_dir:str, num_threads:int = 1):
        # Create a directory for the astronaut dat files
        prepDir(astro_pickle_dir)

        self.parent_dir = '/'.join(train_dir.split('/')[0:-2])
        self.cache_dir = self.parent_dir + '/Temp'
        self.input_cache =  self.cache_dir + '/Photo_Bin'
        self.main_cache = self.cache_dir + "/Input_Cache.dat"

        # Initialize parameters
        self.astro_pickle_dir = astro_pickle_dir
        self.num_threads = abs(num_threads)
        self.known_faces = self.itemizeKnown()
        self.found_faces = {}
        self.found_faces_distance = {}
        self.img_cache = {}
        self.cache_path = self.input_cache + '/'

        # Train the model on all of the faces in the training directory
        self.train(train_dir)

        # Load all photos from the cache
        if os.path.exists(self.main_cache):
            with open(self.main_cache,'rb') as f:
                self.img_cache = pickle.load(f)

    '''
    DESC:   Outputs the found faces

    INPUT:  Self

    OUTPUT: All of the faces found
    '''
    def outputResults(self):
        return self.found_faces

    '''
    DESC:   Resets the list of found faces

    INPUT:  Self

    OUTPUT: None
    '''
    def clearResults(self):
        self.found_faces = {}

    '''
    DESC:   Outputs the found faces and resets found_faces

    INPUT:  Self

    OUTPUT: All of the faces found
    '''
    def purgeResults(self):
        temp = self.found_faces
        self.found_faces = {}
        return temp


    '''
    Function adds astronaut objects to model for every image in the given directory and trains the astonaut object to recognize the face in the image. If an image in the directory already has a corresponding .dat file in astro_pickle_dir, it will be ignored.

    PARAM:
        train_dir: Directory in which all images to be trained on are
        stored. Images must follow this naming convention:
            <first name>_[<middle name>_]<last name>&<nationality>.jpg
    '''
    def train(self,train_dir:str):
        print("Training on all images in {0} using {1} threads".format(train_dir,self.num_threads))

        # Set up multithreading
        semaphore = mp.Semaphore(self.num_threads)
        processes = []
        lock = mp.Lock()

        # Cycle through all jpeg files and train on them
        for filename in os.listdir(train_dir):
            # Checks if jpeg
            if filename.split(".")[-1] != "jpg":
                continue

            lock.acquire()
            print("Training on image:", filename)
            lock.release()

            # Create an astronaut
            astro = self.astroInit(filename)
            if astro == None :
                continue

            if astro.filename in self.known_faces :
                print("\tModel has already been trained on",filename)
                continue

            # Train
            semaphore.acquire()
            p = Process(target = self.addAstro, args = ("{0}{1}".format(train_dir,filename), semaphore,lock))
            processes.append(p)
            p.start()

        # Wait for processes to rejoin
        for proc in processes:
            proc.join()



    '''
    File adds given astronaut object or picture to model.

    PARAM:
        astronaut = Can by of type Astro.Astronaut or str (in which case it
        should be a file path). If it is of type Astro.Astronaut, astronaut
        will be directly added to the model. If it is a filepath, an astronaut
        object will be created, trained on the image, and added to the model.
        Filepath must follow naming conventions outlined in Master_Model.train()
    '''
    def addAstro(self, astronaut, sem:mp.Semaphore, lock:mp.Lock):
        # If the astronaut passed is a person
        if type(astronaut) == Astro.Astronaut:
            # Save their data
            astronaut.saveData(self.astro_pickle_dir)
            # Add to the list of alread-learned faces
            self.known_faces[astronaut.filename] = astronaut.facialData

        # If the astronaut is just a name
        if type(astronaut) == str:
            # Create the astronaut
            astro = self.astroInit(astronaut)

            if(astro == None):
               sem.release()
               return

            # If the astronaut is already known
            if astro.filename in self.known_faces:
                lock.acquire()
                print("\tModel has already been trained on",astronaut)
                lock.release()
                sem.release()
                return

            # Train the model
            astro.trainModel(astronaut,lock)

            if type(astro.facialData) == np.ndarray:
                astro.saveData(self.astro_pickle_dir)
                self.known_faces[astro.filename] = astro.facialData

            sem.release()

    '''
    DESC:   Creates an astronaut object from a filepath to a photo

    INPUT:  A string filepath as `filepath`

    OUTPUT: Astro object
    '''
    def astroInit(self, filepath):
        # Finds the name of the photo from the filepath
        regex_noPath = re.compile(r'\/')
        filename = regex_noPath.split(filepath)[-1]

        # Finds the name and country from the file name
        regex_nc = re.compile(r"&")
        name_country = regex_nc.split(filename)

        # Finds the astroaut's name
        regex_names = re.compile(r"_")
        ident = regex_names.split(name_country[0])

        # Finds the astronaut's coutry
        regex_no_dot = re.compile(r"\.")
        country = regex_no_dot.split(name_country[1])[0]

        # Removes an identifier string from the list of names
        if "cropped" in ident:
            ident.remove("cropped")

        # If there's a middle name, assign it
        if len(ident)==3:
            fName, lName, mName = ident
            return Astro.Astronaut(country,fName,lName,mName)
        # If there's not, don't
        elif len(ident)==2:
            fName, lName = ident
            return Astro.Astronaut(country, fName, lName)
        # If there are the wrong number of names, print an error
        else:
            print("\tERROR: Incorrectly formatted file name: {}\n\tFiles must be named <first name>_<lastname>&country.jpg".format(filename))
            print("\tFile will be ignored")
            return None

    '''
    DESC:   Initializes an astronaut from a filepath and loads their facial data

    INPUT:  A string filepath as `filepath`

    OUTPUT: Astro object
    '''
    def loadAstro(self, filePath):
        # Initializes the astronaut
        a = self.astroInit(filePath)
        directory = getDir(filePath)
        if a == None:
            return None
        a.loadData(directory)
        return a


    '''
    Method searches image for astronaut faces

    Parameters:
        img_path:str = path of image to search for astronaut faces.

    Returns:
        img_entry:dict = Dictionary object consisting of (a:i) pairs where a is
        the found astronaut, i is the index of the face attributed to the
        astronaut. Indicies are generated by the face_recognition library.
    '''
    def findFaces(self,img_path:str, sem:mp.Semaphore, lock:mp.Lock):
        # A dictionary of all of the astronauts found in the photo
        img_entry = {}
        # Unknown faces found
        unknown_encodings = None
        # Location data that hasn't been labled yet
        unknown_locations = []
        # Whether the image is found in the cache
        found_in_cache = False
        # Get the name of the file from path
        img_name = getFileName(img_path)

        picklePath = '{0}/{1}.dat'.format(self.cache_path, img_name.split('.')[0])

        # If we're supposed to look in the cache
        if cache_img:
            if img_name in self.img_cache:
                # Assign already-found encodings
                unknown_encodings = self.img_cache[img_name]
                found_in_cache = True
            elif os.path.exists(picklePath):
                with open(picklePath,"rb") as f:
                    self.img_cache[img_name] = pickle.load(f)
                sem.release()
                return

        # If the image is not in the cache
        if not found_in_cache:
            try:
                unknown_image = face_recognition.load_image_file(img_path)
                # Find dacial encodings and locations from the image
                unknown_encodings, unknown_locations = self.encodeWithRotation(unknown_image)

                # Save the encodings and locations to the cache
                # self.img_cache[img_name] = (unknown_encodings,unknown_locations)
                self.img_cache[img_name] = unknown_encodings

            except IndexError:
                lock.acquire()
                err_log.append("\tI wasn't able to locate any faces in image: {} ... Image will not be included in results".format(img_path))
                lock.release()
                return None

        # Find the distances between every astronaut and every other astronaut
        face_dist = self.custFaceDistance(unknown_locations)

        # For every file in the pickling directory
        for filename in os.listdir(self.astro_pickle_dir):
            fullpath = self.astro_pickle_dir+filename

            # Initialize astronaut
            astro = self.loadAstro(fullpath)
            if astro == None:
                return None

            # Check their face against the encodings and which people match
            found_arr = astro.checkFace(unknown_encodings)

            # Find a list of deltas to the faces
            facailSimilarities = astro.faceDistance(unknown_encodings)

            # Skip the face if no one matched
            if sum(found_arr) == 0 :
                continue
            # If there was a match
            else:
                # Create an entry for the image
                img_entry[astro.filename] = []
                for i in range(len(found_arr)):
                    # Add astronauts to dictionary of people in the image
                    if found_arr[i] != 0:
                        img_entry[astro.filename].append((i,facailSimilarities[i], face_dist))
                        print(img_entry)

        # Pickle the results without repeats
        pickle_obj = (img_name, self.deleteRepeats(img_entry))
        makePickle(self.cache_path,img_name,pickle_obj)
        sem.release()

    '''
    DESC:   Deletes the repeated faces in a photo

    INPUT:  A dictionary of faces, `faces`

    OUTPUT: A dictionary of non-repeated faces
    '''
    def deleteRepeats(self,faces:dict):
        unrepeated_faces = {}
        seen_index = []

        for k_1 in faces:
            for t_1 in faces[k_1]:
                current_index = t_1[0]
                current_distance = t_1[1]
                if current_index in seen_index: continue
                seen_index.append(current_index)
                entry = (k_1,current_index)
                for k_2 in faces:
                    for t_2 in faces[k_2]:
                        if current_index == t_2[0]:
                            if t_2[1]< current_distance:
                                entry = (k_2,current_index)
            if entry[0] in unrepeated_faces:
                if not entry[1] in unrepeated_faces[entry[0]]:
                    unrepeated_faces[entry[0]].append(entry[1])
            else:
                unrepeated_faces[entry[0]] = [entry[1]]
        return unrepeated_faces


    '''
    Method searches all images in given directory for astronaut faces

    Parameters:
        img_dir:str = path to directory containing images to search
        cache_search:bool = True value indicates that dictionary should be
        pickled and stored for future quick retrevial. Only set to false if
        very confident that no images in the directory will be searched again.

        Side-Effect: Adds entries (img: dict) to found_faces dictionary, where
        img is the filepath of an image and the dict is the dictionary returned
        from findFaces(img)

    Returns:
        found_faces = dictionary containing entries (img:dict) as defined in the
        Side-Effects. Note that the returned variable is also an instance
        variable of the class.
    '''
    def findFacesDir(self, img_dir, cache_search = True):
        semaphore = mp.Semaphore(self.num_threads)
        processes = []
        lock = mp.Lock()
        print("Looking for learned faces in all images in {0} using {1} threads".format(img_dir, self.num_threads))
        prepDir(self.cache_path)

        # Cycles through all filenames
        for filename in os.listdir(img_dir):
            # Finds the jpg files
            regex = re.compile(r"\.")
            if regex.split(filename)[-1] != "jpg": continue
            print("Analyzing image",filename)
            fullpath = img_dir+filename
            semaphore.acquire()
            # Creates a list of processes to run the faces
            p = Process(target = self.findFaces, args = (fullpath, semaphore,lock))
            processes.append(p)
            p.start()

        # Join processes
        for proc in processes: proc.join()

        # Load the results of all of the image processing
        self.unpickleResults()
        printErr("While processing the images the following errors occured:")
        if not os.path.isdir("{0}/{1}".format(self.parent_dir, img_dir)):
            os.mkdir("{0}/{1}".format(self.parent_dir, img_dir))

        with open(self.main_cache,"wb") as f:
            pickle.dump(self.img_cache,f)

        return self.found_faces

    '''
    DESC:   Lists all of the astronauts already known

    INPUT:  None

    OUTPUT: A list of known astronauts
    '''
    def itemizeKnown(self):
        #helper method, nothing to see here...
        known_astro = {}
        for filename in os.listdir(self.astro_pickle_dir):
            with open('{0}{1}'.format(self.astro_pickle_dir,filename),'rb') as f:
                known_astro.update(pickle.load(f))
        return known_astro

    '''
    DESC:   Loads all of the results from memory

    INPUT:  None

    OUTPUT: None
    '''
    def unpickleResults(self):
        for filename in os.listdir(self.cache_path):
            with open(self.cache_path + filename,"rb") as f:
                result = pickle.load(f)
                self.found_faces[result[0]] = [result[1]]
        # shutil.rmtree('../Data/Temp/Photo_Bin/')

    '''
    DESC:   Rotates points in a given image a certain number of times. This has
            the effect of turning an xy plane 90º for every rotation specified

    INPUT:  self, the x/y coordinates of a point as `x` and `y`, the image
            that's being referenced as `img`, the number of times to be rotated
            as `times`, and the direction to be rotated as dir

    OUTPUT: A new, rotated, x/y pair of coordinates
    '''
    # Checked in `rotationTest.py` and it works as expected
    def rotateCoordinates90(self, x, y, img, times, dir = "r"):
        x_max, y_max, z_max = img.shape

        if dir == "r":
            times = -times%4
        elif dir == "l":
            times = times%4
        else:
            raise ValueError("\'dir\' must be either \'r\' or \'l\'")

        if times == 0:
            return x,y
        elif times == 1:
            return y, x_max-x
        elif times == 2:
            return x_max-x, y_max-y
        else:
            return y_max-y, x

    '''
    DESC:   Finds all of the facial encodings in an image as well as the
            locations for all of their faces. Includes rotating the image 4
            times to make sure that all faces are found

    INPUT:  self, and the image to be scanned for faces, `img`

    OUTPUT: A list of facial encodings found in the image and a list of face
            locations. The locations are in the format [(x1,y1,x2,y2),...],
            where every tuple is a facial location, and where x1/y1 are the
            bottom left and x2/y2 are the top right of a bounding box around
            the person's face
    '''
    def encodeWithRotation(self, img):
        faces = []
        locs = []

        for i in range (0,4):
            # Accoring to the docs, np.rot90 rotates to the left by default,
            # which is the same as in our test
            imgSub = np.rot90(img, k=i)
            # Find the face locations in each revolution of the photo
            loc = face_recognition.face_locations(imgSub)
            # Grab all of the visible face encodings
            faces += face_recognition.face_encodings(imgSub)
            # Rotate the facial locations
            locs += self.rotateAllLocations(loc, img, i)

        return faces, locs

    '''
    DESC:   Takes a given image and list of facial locations and returns the
            rotated version of those encodings

    INPUT:  self, a list of facial bounding box locations as `locations`, the
            image being used for reference as `img`, and the number of times
            that the points are to be rotated as `times`

    OUTPUT: A list of new facial locations that have been rotated the
            appropriate number of times
    '''
    def rotateAllLocations(self, locations, img, times):
        newEncodings = []
        # Updates every rectangle (x1,y1,x2,y2) in locations
        for rect in locations:
            # Appends the rotated coordinates to the list of new encodings
            # Since the image rotates left every time, we want to rotate the
            # opposite direction (right), which is the default
            newEncodings.append(self.rotateCoordinates90(rect[0], rect[1], img, times)+
            self.rotateCoordinates90(rect[2], rect[3], img, times));

        return newEncodings

    '''
    DESC:   Calculates the distance between each face and every other face in
            the given photo

    INPUT:  self, a list of astronaut facial coordinates (lower left corner and
            upper right corner of a facial bounding box) labled
            `listOfAstroCoords`. The format for this list it
            [(x1,y1,x2,y2),...], where 1 is the bottom left and 2 is the top
            right of the box.

    OUTPUT: A list of distances between each astronaut and every other
            astronaut. The list is in the format [[d1,...,dn],...], where every
            index of the outer list cooresponds to an astroaut found in the
            image, and every element of the inner list cooresponds to an
            astronaut. The astronauts in the same order in both the inner and
            outer list, so astronaut at index [n] of the outer list would be at
            index [n][n] of the outer list.
    '''
    def custFaceDistance(self, listOfAstroCoords):
        if listOfAstroCoords == []: return []

        # Compute the area of each face
        faceArea = np.array([((x[2]-x[0])*x[3]-x[1]) for x in listOfAstroCoords])
        # Compute the average face area
        avgFaceArea = np.sum(faceArea)/len(faceArea)

        # Find the center coordinate of each face
        centers = [[(x[2]-x[0])/2, (x[3]-x[1])/2] for x in listOfAstroCoords]
        distances = []

        # Cycle through the center points for every astronaut
        for x1,y1 in centers:
            # Holds the distances relative to the current astronaut
            tempDistances = []
            # Cycle through the center points for every astronaut again
            for x2,y2 in centers:
                # Compute the spatial euclidian distance between the given
                # facial centerpoints
                distance = ((x2-x1)**2+(y2-y1)**2)**(1/2.0)

                # Scale distance by face area to account for distance
                # Farther away = smaller face, closer = larger face
                tempDistances.append(distance/avgFaceArea)
            distances.append(tempDistances)
        return distances
