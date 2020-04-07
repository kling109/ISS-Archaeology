# A program to obtain photographs from flickr.  Specifically, the
# program will obtain photos of astronauts on the ISS, then return
# each image accompanied by a description of who's in the photo.

import flickr_api as flickr
import webbrowser
import sys
import os

API_KEY = u'49f74fc6ce14613394717c0802508ba0'
API_SECRET = u'd0e40a7e772a3f61'

def initialize():
    '''
    Prepares the flickr API to get photos.
    '''
    flickr.set_keys(api_key = API_KEY, api_secret = API_SECRET)
    flickr.set_auth_handler(".authFile.txt")

def getUser(username: str):
    '''
    Gets the user id by using the username.

    Keyword Arguments:
    username (string): The user to search for.

    Returns:
    user (obj): a Flickr API user object for the given username.
    '''
    return flickr.Person.findByUserName(username)

def getImagesFromAlbum(user, album : str):
    '''
    Gets the images from a user's albums.  The images
    are written to a new directory with the name of the
    album, along with the descirptions.

    Keyword Arguments:
    user (obj): a Flickr API user object
    album (string): a specific album name

    '''
    idx = None
    photosets = user.getPhotosets()
    for id,info in enumerate(photosets):
        if (info.title == album):
            idx = id
    if (idx != None):
        albumPhotos = photosets[idx]
        if not os.path.exists(albumPhotos.title):
            print("Creating directory " + albumPhotos.title)
            os.mkdir(albumPhotos.title)
        os.chdir(albumPhotos.title)
        for photo in albumPhotos.getPhotos():
            print("Saving photo " + photo.title)
            photo.save(photo.title)
            print("Getting photo information...")
            info = photo.getInfo()['description']
            print("Saving photo information...")
            f = open(photo.title+".txt", "w")
            f.write(info)
            f.close()

def getImages(username : str, album : str):
    '''
    Driver method used to get images from an album.

    Keyword Arguments:
    username (string): The username of the desired user.
    album (string): The name of the desired album to download.
    '''
    initialize()
    user = getUser(username)
    getImagesFromAlbum(user, album)


if __name__ == "__main__":
    '''
    An example of how to use the module.
    '''
    getImages(username = "NASA on The Commons", album = "Apollo 1")
