'''
@author:    Matt Raymond
@desc:      This file contains a driver method for Main_Model.py, and is meant
            to simplify implimentation in future code.
'''

import Main_Model
import os
import json
import re


'''
DESC:   Finds all of the directory filepaths that you want to search in

INPUT:  A string filepath to a directory as `directory`, and a bool that
        determines whether you want to recursively include every sub-directory
        in your search as `recursive`

OUTPUT: A list of filepaths
'''
def findDir(directory:str, recursive:bool):
    if recursive:
        folder_list = os.walk(directory)
        return [item[0] for item in folder_list]
    else:
        return [directory]


'''
DESC:   Gets all of the photo data in the given directory

INPUT:  A instance of Main_Model as `model`, a string directory to search in as
        `directory`, and a bool that determines whether you want to
        recursively include every sub-directory in your search as `recursive`

OUTPUT: A list of photo data
'''
def getPhotoData(model:Main_Model, directory:str, recursive:bool):
    photos = {}
    for f in findDir(directory, recursive):
        model.findFacesDir(f + "/")
        photos[f] = model.purgeResults()
    return photos

'''
DESC:   Trains the model, scans all of the photo data in a directory, and
        dumps the data to a specified directory

INPUT:  A string filepath to the directory that contains the photos of
        astronauts that you want the model to train on as `trainDir`, a string
        filepath to the directory that contains the new photos to be scanned
        as `dataDir`,a string filepath where all of the pickled data should be
        stored as `pickleDir`, an int for the number of threads to be used for
        multithreading as `numThreads`, a string filepath to a directory that
        will be used to save all of the dumped files as `dumbDir`, and a bool
        that determines whether you want to recursively include every
        sub-directory in your search as `recursive`

OUTPUT: None
'''
def runModel(trainDir:str, dataDir:str, pickleDir:str, numThreads:int = 4, dumpDir:str = "../Data/Scan_Result", recursive:bool = False):
    if trainDir[-1] != "/": trainDir += "/"
    if pickleDir[-1] != "/": pickleDir += "/"

    model = Main_Model.Master_Model(trainDir, pickleDir, numThreads)
    photos = getPhotoData(model, dataDir, True)

    if not os.path.exists(dumpDir):
        os.makedirs(dumpDir)

    for key in photos.keys():
        # Find the name of the lowest level directory
        dir = re.compile(r"/").split(key)[-1]
        if(dir == ""): dir = "origin"
        with open('{0}/{1}_result.json'.format(dumpDir, dir), 'w') as fp:
            json.dump(photos[key], fp)

if __name__ == "__main__":
    runModel(trainDir = "../Data/Portraits", dataDir = "../Data/Test_Input",
        pickleDir = "../Data/Temp/Portrait_Bin", numThreads = 8, recursive = True)
