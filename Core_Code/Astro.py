import face_recognition
import pickle
import multiprocessing as mp

'''
A class to allow easy model-training, data-saving, data-loading, and model
classification for each astronaut.
'''
class Astronaut:

    '''
    Constructor

    INPUT:  Country, first name, last name, and middle name as strings. The
            middle name defaults to ""

    OUTPUT: None
    '''
    def __init__(self, country: str, fName : str, lName : str, mName  = ""):
        self.fName = fName
        self.lName = lName
        self.mName = mName
        self.country = country
        self.facialData = None
        self.filename = "{0}_{1}&{2}".format(fName, lName, country)

    '''
    DESC:   Trains the face encodings based on a file, provided by a filepath

    INPUT:  a filepath to the image that will be encoded into facial markers,
            and a lock for multithreading

    OUTPUT: None
    '''
    def trainModel(self, imageFilepath, lock:mp.Lock):
        known = face_recognition.load_image_file(imageFilepath)
        try:
            self.facialData = face_recognition.face_encodings(known)[0]
        except IndexError:
            lock.acquire()
            print("\t WARNING: No faces found in: ",imageFilepath)
            print("\t File will be ignored")
            lock.release()

    '''
    Serializes the astronaut to a binary file using pickle
    Input: a filepath for the location the data will be saved in, taken as a string
           and defaulted to ""
    Output: None
    '''
    def saveData(self, filePath = ""):
        tempDict = {}
        tempDict[self.filename] = self.facialData
        with open("{0}{1}.dat".format(filePath, self.filename), 'wb') as f:
            pickle.dump(tempDict, f)
            f.close()

    '''
    DESC:   Loads the astronaut's information from a binary file provided the filepath

    INPUT:  a filepath for the location the data will be read from, taken as a string
            and defaulted to ""
    OUTPUT: None
    '''
    def loadData(self, filePath = ""):
        tempDict = {}
        with open("{0}{1}.dat".format(filePath, self.filename), 'rb') as f:
           tempDict = pickle.load(f)
           f.close()
        self.facialData = tempDict[self.filename]

    '''
    DESC:   Searches for matches when given a list of astronaut facial encodings from a photo

    INPUT:  a list of facial data

    OUTPUT: a list of found astronauts
    '''
    def checkFace(self, listOfAstronauts):
        FoundAstronauts = []
        for face in listOfAstronauts:
            FoundAstronauts.append(face_recognition.compare_faces([self.facialData], face)[0])
        return FoundAstronauts


    '''
    DESC:   Finds the euclidian distance between self.facialData facial encoding
            and a list of astronaut facial encodings from a photo

    INPUT:  a list of facial data

    OUTPUT: a list of the euclidian distances
    '''
    def faceDistance(self, listOfAstronauts):
        FoundAstronauts = []
        for face in listOfAstronauts:
            FoundAstronauts.append(face_recognition.face_distance([self.facialData], face)[0])
        return FoundAstronauts
