# ISS-Archaeology - Analysis of Astronaut Interactions
Matt Raymond, Daniel Briseño, Trevor Kling, and Greg Albarian

This project was produced in conjunction with [Chapman University](http://chapman.edu) and [ISS Archeology](https://issarchaeology.org/).

## Background
Due to NASA's vigilent data collection, there are thousands of photos of astronauts aboard the ISS. Our group hopes to combine data mining, machine learning, and contemporary archeology to better understand the intercultural and interpersonal interactions between astronauts aboard the ISS. That data will serve to improve the emotional ergonomics of future deep-space craft, allowing ship designs to improve crew moral and comfort rather than undermine it.

## Plan (January Term)
Since we only had one month to work on this project, we had to break it down into a few simplified steps:
- For each photo, log which astronauts appear in photos together
- Compute the common pairings
- Create a relationship graph to display the results
- Perform market-basket analysis to find the common pairings
- Research the astronauts from the market-basket analysis to determine potential causes for the pairings

## Implimentation (January Term)
We utilized the following libraries:
- `pickle`
  - Serialization of astronaut classes to a binary file
- `face_recognition`
  - Encoded facial data for astronauts and photos
- `apyori`
  - Performed market basket analysis
  
We created [this](https://drive.google.com/open?id=1wijdtXajYYc4m4TwJby97zHEIzCoy-Qr) dataset in order to train our astronaut classifier. We release it free to use with credit.

Error minimization was tested by cross-referencing our results against manually-classified data until we got a nearly-perfect score.

## Result (January Term)

### Legend
<img src="https://github.com/kling109/ISS-Archaeology/blob/master/Facial_Recognition_Model/Legend.png?raw=true" alt="drawing" width="400"/>

**All Pairings from Image Scans**
![All Pairings](https://github.com/kling109/ISS-Archaeology/blob/master/Facial_Recognition_Model/astronautrelations.png?raw=true)
From a cursory glance, we can see that the Americans are highly interconnected, as well as tied to most of the Russians and a few of the Japanese. However, there are very few connections between Russians, or between astronauts of other nationalitie to each other. Overall though, this image is very crowded and difficult to analyze.

We can clear this image up a bit by performing market basket analysis on our pairings.

**Frequent Pairings from Market Basket Analysis**
![Market Basket Analysis](https://github.com/kling109/ISS-Archaeology/blob/master/Facial_Recognition_Model/freqrelations.png?raw=true)
Now we can see the most common connections between astronauts, and we can see a few things that stand out. For example, Yuri Usichev is photographed very often with many American astronauts, while Ronald Garan is often with two cosmonauts. One possible explination for this is that Garan is Roman Catholic, and therefor would likely be more at home with the cosmonauts (who tend to be Greek Orthodox) rather than the more protestant Americans. However, this is just an exploratory theory.

## Issues (January Term)
Our biggest problem was taht the pre-trained model we implimented (`face_recognition`) was unable to distinguish between people who were not caucasian. Our model worked well with white astronauts, but it classified all astronauts of Asian descent as the same person.

We're not exactly sure why that is, but [it's a common problem with facial recognition models in general](https://towardsdatascience.com/bias-in-machine-learning-how-facial-recognition-models-show-signs-of-racism-sexism-and-ageism-32549e2c972d?gi=43f55d4d5ea3), so we assume it stems from one of the mode common problems: a non-representative training set. If this model was trained on mainly people of caucasian descent, then it would have learned non-universal face markers, leading to an over-fit model that would perform poorly on anyone else.

However, we were able to get around this problem by modifying the way we matched faces. We still utilixed `face_recognition`'s built-in `compare` function, but if we found one photo that was classified as more than one astronaut, we calculated the euclidian distance between the unknown face and all suspected matches, and chose the face that returned the smallest value. Although not ideal, this allowed us to perform accurate facial recognition with a model that was not originally successful.

## Future Exploration (Spring Term)
In the future, we want to expand the scope of our model and research:
- Normalize the dataset
  - Currently, the market-basket analysis doesn't take into account the amount of time each astronaut spent in space, so results can be skewed. For example, if one astronaut takes a lot of photos in a day, while another astronaut takes only a few photos in a year, the results will be skewed in favor of the first.
- Perform nalysis on a larger dataset
  - Our current dataset is derived from NASA's public Flickr account. This is a good starting point, but means that our data is heavily skewed toward what NASA wants the public to see, as well as skewed towards the American perspective in general. By introducing datasets from other space agencies, we would be able to provide a more objective view into life aboard the ISS.
- Add additional graphs classifying astronauts based on things like religion and sex, and see how those might influence interactions.
- Expand our model to analyze how astronauts interact with ground-crew members.

Our final presentation can be found [here](http://docs.google.com/presentation/d/1_WmAVsl9I-yZEdyam6LzORiehsni7n3AUBXyfy71CNA/edit?usp=sharing).

## Model Demo

- To demo model: From the Facial_Recognition_Model subdirectory, run `python3 Main.py`
- To use model in code: Add `from Main_Model import Master_Model` to top of .py file (file must be located in Facial_Recognition_Model folder) and initialize an instance of `Master_Model` and call :
```
    model = Master_Model(train_dir, astro_pickle_dir, num_threads = 1)
    results = model.findFacesDir(test_dir)
```
  - Where:
    - train_dir:str = directory containing pictures of all astronauts to be added to model. Picture files must follow the following naming convention: `<first name>_[<middle name>_]<last name>&<nationality>.jpg`

    - astro_pickle_dir:str = Directory in which face_recognition model objects will be flattened and saved as .dat files. Note that any .dat files in this directory will be added to model

    - num_threads:int = Number of threads to be used by the model during training and analysis
    - test_dir = directory of jpg files in which to look for astronauts
  - Note that the return value of Master_Model.findFacesDir is an instance variable of the Master_Model class (Master_Model.found_faces) and will therefore be updated by repeated calls to findFacesDir. Entries in found_faces generated by previous calls to findFacesDir will NOT be deleted by any subsequent calls, and this will be reflected in the return value of findFacesDir.
- To run market-basket analysis on the output from Main_Model, use the .ipynb file Facial_Data_Generation.ipynb located in the Facial_Recognition_Model subdirectory.

## Scripts
### Flickr API
To user the `flickriss.py` module, follow the steps in the tutorial [here](https://github.com/alexis-mignon/python-flickr-api/wiki/Flickr-API-Keys-and-Authentication).

### classification.html
An html page with embeded javascript that we used as a tool for classing the astronauts' sex as `m` or `f`. We didn't end up using the result.
- Press `m` to mark the astronaut as male
- Press `n` to mark the astronaut as female
- Press `space` to print the output to the console (since javascript can't save to a file)
- Press `u` to undo the last action (not fully implimented because it ended up not being needed)

### Facial_Recognition_Model
**This information needs to be filled out still**
- Say something about how our program works by creating one model per astronaut

## Files
### astroSex.csv
A csv file that holds astronaut names and the sex assigned to them (did not end up being used in the analysis)

### cropped_Astronaut_photos/*.jpg
A dataset of cropped versions of the `ISS_Astronaut_photos/*.jpg` dataset. This was originally going to be used to reduce the training time of the models, but then we realized that we could use `pickle` to serialize the model data instead. Now we're saving it for future projects in case they want smaller files to train their model on.

The nameing convention is the same as `ISS_Astronaut_photos/*.jpg`, but `cropped_` was added to the bedinning of every filename.

### ISS_Astronaut_photos/*.jpg
A dataset manually built by Matt, Trevor, and Daniel from NASA's website. the naming convention for each file is `<first_name>_<last_name>&<country>.jpg`. The `country` tag was added to simplify the process of classifying astronauts by country.

## Classes
### Astro.py
A class to allow easy model-training, data-saving, data-loading, and model classification for each astronaut.
#### Variables
- `self.fName`: `str`, no default, represents the astronaut's first name
- `self.lName`: `str`, no default, represents the astronaut's last name
- `self.mName`: `str`, defaults to `""`, represents the astronaut's middle name
- `self.country`: `str`, no default, represents the astronaut's host country
- `self.facialData`: `face_encoding`, defaults to `None`, holds the trained model
- `self.filename`: `str`, defaults to `"{0}_{1}&{2}".format(fName, lName, country)`, Is the filename of the astronaut's data
  - This variable is no longer needed, as all astronauts are saved into one file. We originally thought the encodings were going to be much larger than they were and that we were going to need to load and unload the astronauts individually, but the encodings were so small that we decided to save all of the astronauts in one file.
#### Functions
`__init__(self, country: str, fName : str, lName : str, mName  = "")`
- Initializes the astronaut object
- No return value

`trainModel(self, imageFilepath, lock:mp.Lock)`
- Trains the face encodings based on a file, provided by a filepath
- No return value

`saveData(self, filePath = "")`
- Serializes the astronaut to a binary file using pickle
- No return value

`loadData(self, filePath = "")`
- Loads the astronaut's information from a binary file provided the filepath
- No return value

`checkFace(self, listOfAstronauts)`
- Searches for matches when given a list of astronaut facial encodings from a photo
- Returns an array of the found astronauts

`faceDistance(self, listOfAstronauts)`
- Finds the euclidian distance between `self.facialData` and a list of astronaut facial encodings from a photo
- Returns an array of distances

## JsonFlags.py only in GregoryBranch
it gets an OS error thats states:  
OSError: [Errno 24] Too many open files  
in order to run this code the test directory needs  
the pictures from the Dropbox or Flickr

