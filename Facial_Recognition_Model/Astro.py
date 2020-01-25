import face_recognition
import pickle
import multiprocessing as mp



class Astronaut:
    
    def __init__(self, country: str, fName : str, lName : str, mName  = ""):
        self.fName = fName
        self.lName = lName
        self.mName = mName
        self.country = country
        self.facialData = None
        self.filename = "{0}_{1}&{2}".format(fName, lName, country)
        
    def trainModel(self, imageFilepath, lock:mp.Lock):
        known = face_recognition.load_image_file(imageFilepath)
        try:
            self.facialData = face_recognition.face_encodings(known,num_jitters=5)[0]
        except IndexError:
            lock.acquire()
            print("\t ERROR: No faces found in: ",imageFilepath)
            print("\t File will be ignored")
            lock.release()
    
    def saveData(self, filePath = ""):
        tempDict = {}
        tempDict[self.filename] = self.facialData
        with open("{0}{1}.dat".format(filePath, self.filename), 'wb') as f:
            pickle.dump(tempDict, f)
            f.close()
            
    def loadData(self, filePath = ""):
        tempDict = {}
        with open("{0}{1}.dat".format(filePath, self.filename), 'rb') as f:
           tempDict = pickle.load(f)
           f.close()
        self.facialData = tempDict[self.filename]
    
    def checkFace(self, listOfAstronauts):
        FoundAstronauts = []
        for face in listOfAstronauts:
            FoundAstronauts.append(face_recognition.compare_faces([self.facialData], face)[0])
        return FoundAstronauts

    def faceDistance(self, listOfAstronauts):
        FoundAstronauts = []
        for face in listOfAstronauts:
            print(type(self.facialData))
            FoundAstronauts.append(face_recognition.face_distance([self.facialData], face)[0])
        return FoundAstronauts