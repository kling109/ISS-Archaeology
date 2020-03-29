'''
@author:    Matt Raymond
@desc:      This file contains a driver method for our apriori algorithm, and is
            meant to simplify implimentation in future code
'''

import Main_Model
import os
import json
from apyori import apriori
import re # might be able to remove


'''
DESC:   Loads all of the photo data from the given directory and returns it in
        a dictionary

INPUT:  sourceDir:str
            - Where the jsons of photo data will be found
        verbose:bool = False
            - Whether the function will output a status of what it's doing

OUTPUT: Returns a dictionary where the keys are photo names and the values are
        lists of astronauts in the photo
'''
def loadPhotos(sourceDir:str = './dumpDir', verbose:bool = False):
    photos = {}

    if verbose:
        print("Loading files:")

    # Get all json files in the directory
    files = [f for f in os.listdir(sourceDir) if ".json" in f]

    #  If there are no json files
    if verbose and not files:
        print("\tNone")
        return {}

    # Cycle through all jjson files
    for file in files:
        # Find the partially-qualified filepath
        fp = sourceDir + "/" + file
        # Open file and read data
        with open(fp) as jsonfile:
            data = json.load(jsonfile)

            # Break up by photo and add to photos dictionary
            for k in data.keys():
                photos[k] = data[k]
                if verbose:
                    print("\t" + k)

    return photos


'''
DESC:   Gets lists of astronauts in each photo

INPUT:  photos:dict
            - A dictionary of photo data

OUTPUT: A list of lists, where each inner list is a list of astronauts in each
        photo
'''
def generateTransactions(photos:dict):
    transactions = []
    # Cycles through all of the photos
    for k in photos.keys():
        # Grabs the lists of astronauts in each photo
        transactions += [[k2 for k2 in list] for list in photos[k]]

    return transactions


'''
DESC:   Removes all the transactions which do not contain any astronaut names

INPUT:  transactions:list
            - A list of lists, where each inner list is a list of astronauts in
            each photo

OUTPUT: A list in the same format as the input, but with no empty sub-lists
'''
def cleanTransactions(transactions:list):
    finalTransactions = []
    for i in transactions:
        if len(i) > 0:
            finalTransactions.append(i)

    return finalTransactions


'''
DESC:   Applies an apriori Market Basket Analysis algorithm to find the most
        frequent pairs. The minsupport is set to a very low value, as only a few
        of the photos will contain any specific astronaut. We then use a very
        high min confidence, to ensure the model is quite sure the relationship
        is correct.

INPUT:  transactions:list
            - A list of lists, where each inner list is a list of astronauts in
            each photo

OUTPUT: A dictionary that contains all of the apriori data
'''
def runApriori(transactions:list):
    return list(apriori(transactions, min_support=0.01, min_confidence=0.80,
        min_lift=1.0, max_length=None))


'''
DESC:   Parse the information out of the apriori results

INPUT:  results:list
            - The results from the apriori algorithm
        save:bool = False
            - Whether the data should be saved in a file
        fileName:str = "frequentPairs"
            - The filepath for the data to be saved in. Should not contain a
            file extension

OUTPUT: Returns a dictionary of frequent pairs/items
'''
def findFrequentItems(results:list, save:bool = False, fileName:str = "frequentPairs"):
    frequentItems = {}
    for r in results:
        # Pull out names of each astronaut in a pair
        names = [x for x in r[0]]
        pair = str((names[0], names[1]))

        # If the pair isn't in the results, add them and their information
        if pair not in results:
            frequentItems[pair] = {}
            frequentItems[pair]["support"] = r[1]
            frequentItems[pair]["confidence"] = r[2][0][2]
            frequentItems[pair]["lift"] = r[2][0][3]

        # If there's a higher confidence level somewhere, replace the values
        # with that one
        elif r[2][0][2] > results[pair]["confidence"]:
            frequentItems[pair]["support"] = r[1]
            frequentItems[pair]["confidence"] = r[2][0][2]
            frequentItems[pair]["lift"] = r[2][0][3]

    if save:
        # Save the frequent pairs data to a json
        with open('{0}.json'.format(fileName), 'w') as fp:
            json.dump(frequentItems, fp)

    return frequentItems


'''
DESC:   Find the raw freqencies at which astronauts are found

INPUT:  photos:dict
            - A dictionary of photos that has been loaded in
        save:bool = False
            - Whether the result should be saved to a json file
        fileName:str = "rawFrequencies"
            - The filename of the file that the results will be saved in

OUTPUT: A dictionary where keys are astronaut names and values are the
        frequencies that they are found in
'''
def findRawFrequencies(photos:dict, save:bool = False, fileName:str = "rawFrequencies"):
    frequencies = {}
    for astros in photos.values():
        for astro in astros[0].keys():
            # If the astro is not in the dictionary, add them
            if astro not in frequencies:
                frequencies[astro] = 1
            # If they are, add one to their frequency
            else:
                frequencies[astro] += 1

    if save:
        # Save the frequencies at which pairs appear to a json
        with open('{0}.json'.format(fileName), 'w') as fp:
            json.dump(frequencies, fp)

    return frequencies


'''
DESC:   Runs the entire model and returns the results

INPUT:  apriori:bool = True
            - Whether the apriori algorithm should be run and return a value
        fItems:bool = True
            - Whether the frequent items from the apriori algorithm should be
            returned
        rawF:bool = True,
            - Whether the raw frequencies of astronauts should be found and
            returned
        sourceDir:str = './dumpDir'
            - Where the photo data was saved in json format. Will only go one
            directory deep (will not search sub-directories)
        verbose:bool = False
            - Whether the program should output information on what it's doing
        saveFreq:bool = False,
            - Whether the frequent items data should be saved
        freqFileName:str = "frequentPairs"
            - Where the frequent items data should be saved
        saveRawFreq:bool = False,
            - Whether the raw frequencies data should be saved
        rawFreqFileName:str = "rawFrequencies"
            - Where the raw frequencies data should be saved

OUTPUT: A dictionary that contains the information specified by the boolean
        parameters
'''
def runModel(apriori:bool = True, fItems:bool = True, rawF:bool = True,
    sourceDir:str = './dumpDir', verbose:bool = False, saveFreq:bool = False,
    freqFileName:str = "frequentPairs", saveRawFreq:bool = False,
    rawFreqFileName:str = "rawFrequencies"):

    # Skips the entire thing if the flags indicate nothing should be run
    if not (apriori or fItems or rawF): return {}

    returnValue = {}
    photos = loadPhotos(sourceDir, verbose)
    transactions = generateTransactions(photos)
    transactions = cleanTransactions(transactions)

    if apriori or fItems:
        results = runApriori(transactions)
        if fItems:
            returnValue["frequentItems"] = findFrequentItems(results, saveFreq, freqFileName)
        if apriori:
            returnValue["apriori"] = results

    if rawF:
        returnValue["rawFreq"] = findRawFrequencies(photos, saveRawFreq, rawFreqFileName)

    return returnValue



if __name__ == "__main__":
    print(runModel())
