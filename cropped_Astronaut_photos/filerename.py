from os import listdir
from os import path
from os.path import isfile, join
import os
mypath = "C:/Users/brise/Documents/AstronautPics"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
for f in onlyfiles:
    src = path.realpath(f)
    os.rename(f, f.lower())

