'''
@author:    Driver method by Matt Raymond, original code by Trevor Kling
@desc:      This file contains a driver method for our graphing system, and is
            meant to simplify implimentation in future code
'''
import json
import glob
import PIL
from PIL import Image
import matplotlib
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import networkx as nx
import numpy as np
import os
import Market_Basket_Driver as mbd


'''
DESC:   Get a dictionary of all names, indexed by their country

INPUT:  data:dict
            - Keys are photo names, values are dictionaries such that keys are
            astronaut names and values are their index in the image

OUTPUT: A dictionary such that keys are country names and the values are lists
        of astronaut names
'''
def namesByCountry(data:dict):
    names = {}

    # Cycles through collections of astronauts, seperated by photo
    for astros in data.values():
        # For every astro
        for item in astros.keys():
            name = item.split('&')[0]
            country = item.split('&')[1]

            # ToDO: Replace this workaround
            if country == "canda":
                country = "canada"

            if country not in names:
                names[country] = [name.replace('_', ' ')]
            else:
                if name.replace('_', ' ') not in names[country]:
                    names[country].append(name.replace('_', ' '))
    return names

'''
DESC:   Produces a uniform offset for a point.  Essentially just a uniform
        number generator.

INPUT:  num:float
            - The number of columns to generate
        diam:float
            - The diameter of the random offset

OUTPUT: A list of x/y coordinates
'''
def getRandOffset(num:float, diam:float):
    coords = []
    row = int(np.sqrt(num))
    for i in range((int(num/row))+1):
        for j in range(row+1):
            coords.append([(diam/row)*i,(diam/row)*j + 2*i])

    return coords


'''
DESC:   Grabs the path to every .jpg/.jpeg image file

INPUT:  fp:str
            - A filepath to search in

OUTPUT: A list of photos
'''
def grabPhotos(fp:str):
    return [f for f in glob.glob(fp + '*.jpg')] + [f for f in glob.glob(fp + '*.jpeg')]


'''
DESC:   Rescales the photos to be a specific dimension.  Maintains the aspect
        ratio of the original photo.

INPUT:  file:str
            - A filepath to an image
        baseWidth:int = 128
            - The width the image should be after the transformation
        savePath:str = './resized_photos/resized_'
            - The path that the image should be saved to after resizing

OUTPUT: None
'''
def scalePhoto(file:str, baseWidth:int = 128, savePath:str = '../Data/Resized_Portraits'):
    savePath += os.sep+'resized_'
    print(file)
    name = file.split('&')[0].replace('_', ' ')
    print(name)
    im = Image.open(file)

    wpercent = (baseWidth / float(im.size[0]))
    hsize = int((float(im.size[1]) * float(wpercent)))

    re = im.resize((baseWidth, hsize), PIL.Image.ANTIALIAS)
    re.save(savePath + file.split(os.sep)[-1])

'''
DESC:   Takes each photo and assigns it to a respective astronaut.

INPUT:  path:str = 'resized_photos/'
            - Where to load the images from

OUTPUT: A dictionary of astronauts and their respective images
'''
def assignPhotos(path:str = '../Data/Resized_Portraits/'):
    if not os.path.exists(path): raise OSError('\"{0}\" does not exist'.format(path))

    img = {}
    files = [f for f in glob.glob(path + '*.jpg')] + [f for f in glob.glob(path + '*.jpeg')]
    for f in files:
        name = f.split('&')[0].split('_')
        img[name[-2] + " " + name[-1]] = mpimg.imread(f)

    return img

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
def loadPhotos(sourceDir:str = '../Data/Scan_Result', verbose:bool = False):
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
                photos[k] = data[k][0]
                if verbose:
                    print("\t" + k)

    return photos


'''
DESC:   Gets frequent pairings from a json file

INPUT:  pfp:str = 'frequentpairs.json'
            - Filepath to the pairs file

OUTPUT: A list of frequent pairings
'''
def getFreqPairs(pfp:str = '../Data/frequentpairs.json'):
    # Get data from file
    with open(pfp) as jsonfile:
        freqdata = json.load(jsonfile)

    # Creates a list of frequent pairings
    fpairs = []
    for nameSet in freqdata.keys():
        name1 = nameSet.split('\'')[1].split('&')[0].replace('_', ' ')
        name2 = nameSet.split('\'')[-2].split('&')[0].replace('_', ' ')
        if name1 not in fpairs:
            fpairs.append(name1)
        if name2 not in fpairs:
            fpairs.append(name2)

    return fpairs


'''
DESC:   Uses the networkx phython library to produce the relations graph for all
        astronauts

INPUT:  names:dict
            - A dictionary where keys are countries and values are lists of
            astronaut names
        img:dict
            - A dictionary where keys are astronaut names and values are
            images associated with those astronauts
        pairs:dict
            - Pairings of astronauts
        save:bool = True
            - Whether the graph should be saved
        fp:dict = None
            - The set of frequent pairings to apply
        show:bool = False
            - Whether the graph should be displayed
        ofp:str = "astronautrelations.png"
            - The name the graph will be saved under

OUTPUT: None
'''
def graphData(names:dict, img:dict, pairs:dict, fp:dict = None, save:bool = True,
              show:bool = False, ofp:str = "../Data/Astronaut_Relations",):

    # print(img)

    astronauts = nx.Graph()
    nodes = []
    node_colors = []
    offsets = []
    labels = {}
    pos = {}
    i = 0
    j = 0

    initial = (0,0)

    DIAMS = [(len(names[k])**(5/9))*20 for k in names.keys()]

    num = int(len(names.keys())**(1/2))+1

    CENTROIDS = []

    offset = max(DIAMS)
    x_pos = 0
    y_pos = 0

    cont = True
    for x in range(num):
        for y in range(num):
            if(x*num+y >= len(DIAMS)):
                cont = False
                break
            CENTROIDS.append((x_pos, y_pos))
            y_pos += offset*1

        if not cont: break

        x_pos += offset*1.2
        y_pos = 0

        offset = max(DIAMS[x*num:])


    NAMES = list(names.keys())

    # for country in list(names.keys()):
    #     centroi

    # Each centroid, diam, and color corresponds to a specific country
    # CENTROIDS = [(200, 500), (100, 100), (500, 500), (500, 200), (125, 400),
                 # (550, 300), (390, 150), (400, 255), (400, 570), (400, 600),
                 # (400, 595)]
     # ['russia', 'usa', 'kazakhstan', 'greatbritain', 'japan', 'italy', 'netherlands', 'canada', 'brazil']
    # DIAMS = [130, 230, 20, 20, 50, 20, 20, 20, 20, 20, 20]
    COLORS = ['#cc0000', '#cc9900', '#009900', '#990099', '#6600ff', '#339966',
              '#663300', '#99cc00', '#727072', '#669999', '#993333']

    for country in list(names.keys()):
        width = DIAMS[i]
        col = COLORS[i]
        offsets += getRandOffset(len(names[country]), width)[0:len(names[country])]
        for n in names[country]:
            if fp is None or n in fp:
                centroid = CENTROIDS[i]
                (randX, randY) = offsets[j]
                pos[n] = np.array([(centroid[0] + randX), (centroid[1] + randY)])
                labels[n] = n
                nodes.append(n)
                node_colors.append(col)

                j += 1
        i += 1

    # Initializes the graph and places each of the nodes.
    plt.figure(3,figsize=(60,60))
    astronauts.add_nodes_from(labels)
    nx.draw_networkx_nodes(astronauts,
                           pos,
                           node_list=nodes,
                           node_color=node_colors,
                           node_size=1500,
                           alpha=0.8)

    # Creates a connection value for each pair of astronauts that appear
    # together in a photo.
    connections = []
    for nameSet in pairs.keys():
        name1 = nameSet.split('\'')[1].split('&')[0].replace('_', ' ')
        name2 = nameSet.split('\'')[-2].split('&')[0].replace('_', ' ')
        connections.append((name1, name2, {}))

    # Draws each edge onto the graph
    astronauts.add_edges_from(connections)
    nx.draw_networkx_edges(astronauts,
                           pos,
                           edgelist=connections,
                           edge_color='#900000',
                           alpha=0.5)

    # Creates the labels for each astronaut, superimposing their faces as well as
    # creating a text label
    ax = plt.gca()
    fig = plt.gcf()
    imsize = 0.02
    trans =  ax.transData.transform
    trans2 = fig.transFigure.inverted().transform
    i = 0

    for n in astronauts.nodes():
        (x, y) = pos[n]
        xx, yy = trans((x, y))
        xa, ya = trans2((xx, yy))
        a = plt.axes([xa-imsize/2.0, ya-imsize/2.0, imsize, imsize])
        a.imshow(img[n])
        a.set_aspect('equal')
        a.axis('off')
        plt.text(xa+60,ya+152,s=n, bbox=dict(facecolor=node_colors[i], alpha=0.25),horizontalalignment='center',fontsize=16)
        i += 1

    # Saves the image
    if save or show:
        if fp is not None:
            ofp += '_min'

        plt.savefig(ofp + ".png")

    # Workaround because plt.show() causes the program to crash
    if show:
        img = Image.open(ofp + ".png")
        img.load()
        img.show()


'''
DESC:   Generates the relations graph

INPUT:  photoPath:str = '../cropped_Astronaut_photos/'
            - Path to the source photos
        save:bool = True
            - Whether the graph should be saved
        show:bool = True
            - Whether the graph should be displayed
        limit:bool = False
            - Whether the graph should be limited to frequent pairs

OUTPUT: None
'''
def generateGraph(photoPath:str = '../Data/Portraits_Cropped/',
                  save:bool = True, show:bool = True, limit:bool = False):

    # Find all of the stronaut names
    data = loadPhotos()
    names = namesByCountry(data)

    # Assigns photos to astronauts
    files = grabPhotos(photoPath)
    for f in files:
        scalePhoto(f)
    img = assignPhotos()

    # Gets the common pairings
    pairs = mbd.runModel(pairs = True)["pairs"]

    if limit:
        frequentPairs = getFreqPairs()
    else:
        frequentPairs = None

    # Graph the result
    graphData(names, img, pairs, frequentPairs, save, show)



if __name__ == '__main__':
    generateGraph(limit = 1)
