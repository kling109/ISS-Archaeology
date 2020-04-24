import face_recognition
import pickle
import multiprocessing as mp

'''
Project Dependencies: None
'''

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
    def __init__(self, country: str, fName : str, lName : str, mName: str  = "", fData = None, img = None):
        self.fName = fName
        self.lName = lName
        self.mName = mName
        self.country = country
        self.facialData = fData
        self.headshot = img

        # We may want to depricate this
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
    // DEPRICATION WARNING //
    '''
    def saveData(self):
        DeprecationWarning('This function has been depricated because it increases the inter-class dependencies of the code')

    '''
    // DEPRICATION WARNING //
    '''
    def loadData(self):
        raise DeprecationWarning('This function has been depricated because it increases the inter-class dependencies of the code')

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

    '''
    DESC:   Overloads the print function for the class

    INPUT:  Self

    OUTPUT: A string
    '''
    def __str__(self):
        if(self.facialData is None): fd = "No facial data"
        else: fd = "Facial data loaded"

        if(self.headshot is None): hs = "No headshot"
        else: hs = "Headshot included"

        return "{0} {1}\n\t{2}\n\t{3}\n\t{4}\n\t{5}.jpg\n".format(self.fName,self.lName, self.country, fd, hs, self.filename)
