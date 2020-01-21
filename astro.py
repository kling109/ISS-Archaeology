import face_recognition
import pickle

class astro:
    fName = ""
    lName = ""
    mName = ""
    country = ""
    facialData = None
    filename = ""
    
    def __init__(self, country: str, fName : str, lName : str, mName  = ""):
        self.fName = fName
        self.lName = lName
        self.mName = mName
        self.country = country
        self.filename = "{0}_{1}&{2}".format(fName, lName, country)
        
    def trainModel(self, imageFilepath):
        known = face_recognition.load_image_file(imageFilepath)
        self.facialData = face_recognition.face_encodings(known)[0]
    
    def saveData(self, filePath = ""):
        tempDict = {}
        tempDict[self.filename] = self.facialData
        with open("{0}{1}.dat".format(filePath, self.filename), 'wb') as f:
            pickle.dump(tempDict, f)
            
    def loadData(self, filePath = ""):
        tempDict = {}
        with open("{0}{1}.dat".format(filePath, self.filename), 'rb') as f:
           tempDict = pickle.load(f)
        self.facialData = tempDict[self.filename]
    
    def checkFace(self, listOfAstronauts):
        FoundAstronauts = []
        
        for face in listOfAstronauts:
            FoundAstronauts.append(face_recognition.compare_faces([self.facialData], face))
        return FoundAstronauts
