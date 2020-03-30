'''
@author:    Matt Raymond

@desc:      Small script to make sure that we had the same naming conventions
            for the ISS missions as NASA did
'''

import csv
import pandas as pd
import os


def getMissionNames():
    data = pd.read_csv('ISS_Missions.csv')

    names = {}

    for index, row in data.iterrows():
        for k in row:
            names[str(k).replace(" ", "_").lower()] = None

    return list(names.keys())

def getScrappedAstros():
    return [f.split("&", 1)[0].split("|", 1)[0].lower() for f in os.listdir("./ISS_Astronaut_photos") if (".jpeg" in f or ".jpg" in f)]

missionNames = getMissionNames()
missionNames.remove("nan")
missionNames.sort()
scrapedAstros = getScrappedAstros()
scrapedAstros.sort()

for name in missionNames:
    if name not in scrapedAstros:
        print(name)
