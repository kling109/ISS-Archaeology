# ISS-Archaeology
## A repository for the CPSC 393 ISS Archeology Project

- To demo model: From the Facial_Recognition_Model subdirectory, run `python3 Main.py`
- To use model in code: Add `from Main_Model import Master_Model` to top of .py file (file must be located in Facial_Recognition_Model folder) and initialize an instance of `Master_Model` and call :
```
    model = Master_Model(train_dir, astro_pickle_dir, num_threads = 1)
    results = model.findFacesDir(test_dir)
```
  - Where:
    - train_dir:str = directory containing pictures of all astronauts to be added to model. Picture files must follow the following naming convention: 
          - `<first name>_[<middle name>_]<last name>&<nationality>.jpg`

      - astro_pickle_dir:str = Directory in which face_recognition model objects will be flattened and saved as .dat files. Note that any .dat files in this directory will be added to model

      - num_threads:int = Number of threads to be used by the model during training and analysis
      - test_dir = directory of jpg files in which to look for astronauts
  - Note that the return value of Master_Model.findFacesDir is an instance variable of the Master_Model class (Master_Model.found_faces) and will therefore be updated by repeated calls to findFacesDir. Entries in found_faces generated by previous calls to findFacesDir will NOT be deleted by any subsequent calls, and this will be reflected in the return value of findFacesDir.
- To run market-basket analysis on the output from Main_Model, use the .ipynb file Facial_Data_Generation.ipynb located in the Facial_Recognition_Model subdirectory.


To user the `flickriss.py` module, follow the steps in the tutorial [here](https://github.com/alexis-mignon/python-flickr-api/wiki/Flickr-API-Keys-and-Authentication).
