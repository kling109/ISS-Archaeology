from sqlite3 import Connection, Cursor
import sqlite3
from PIL import Image
from Astro import Astronaut
import io
import numpy as np
import os

'''
Project Dependencies:
    - Astro.py
'''

'''
A class to allow easy handling of data with the astronaut class. This class is
dependent on the Astronaut class, but it meant to act as a link between the
database and the Astronaut class, so this is fine.
'''
class Astro_Handler:
    def __init__(self, con_string: str):
        '''
        DESC:   Constructor

        INPUT:  con_string: str
        - A filepath to the sqlite database being used

        OUTPUT: None
        '''

        # Checks to see if the database already exists
        exists = os.path.isfile(con_string)

        # Creates a connection to the db
        # If the file doesn't already exist, then it's created
        self.conn = sqlite3.connect(con_string)
        self.curs = self.conn.cursor()

        # If the file didn't exist until just now, then it didn't contain
        # a database
        if not exists: self.create_database()

    def __del__(self):
        '''
        DESC:   Destructor

        INPUT:  None

        OUTPUT: None
        '''

        # Makes sure that the attribute exists before trying to delete
        if(hasattr(self, 'conn')): self.conn.close()

    def create_database(self):
        '''
        DESC:   Initializes the tables and relationships in the sqlite database

        INPUT:  None

        OUTPUT: None
        '''

        # SQL queries ==========================================================
        create_countries = '''create table if not exists Countries(
    	Full_Name varchar(32) unique,
    	Abr_Name varchar(8) primary key
        );'''

        create_astros = '''create table if not exists Astros(
    	F_Name varchar(32) not null,
    	L_Name varchar(32) not null,
    	Headshot blob default null,
    	Facial_Encoding blob default null,
    	Country varchar(8) references Countries,
    	primary key (F_Name, L_Name)
        );'''

        create_photos = '''create table if not exists Photos (
        	File_Name varchar(128) not null
        		primary key
        );'''

        create_links = '''create table if not exists Photo_Link (
    	Photo_Name integer not null references Photos,
    	Astro_F_Name integer not null,
    	Astro_L_Name integer not null,
    	primary key (Photo_Name, Astro_F_Name, Astro_L_Name),
    	foreign key (Astro_F_Name, Astro_L_Name) references Astros
        );'''
        # End of queries =======================================================

        queries = [create_countries, create_astros, create_photos, create_links]
        for q in queries: self.curs.execute(q)

        self.conn.commit()

    def insert_astro(self, astro: Astronaut, commit: bool = True):
        '''
        DESC:   Inserts a single astronaut into the database

        INPUT:  astro: Astronaut
        - An Astronaut object that holds the data to be inserted into the
        database

        commit: bool = True
        - Whether the insert should be commited or not. It should be
        commited any time you want to save data. However, this can
        take up time, and for a group of inserts, it can be left out
        until the last insert.

        OUTPUT: None
        '''

        # SQL queries ==========================================================
        checkCountry = '''select * from Countries where Abr_Name like ?;'''

        checkAstro = '''select * from Astros where F_Name like ? and L_Name like ?;'''

        insertAstro = '''insert into Astros (F_Name, L_Name, Country, Facial_Encoding, Headshot)
        values (?, ?, ?, ?, ?);
        '''

        insertCountry = '''insert into Countries (Abr_Name)
        values (?);
        '''
        # End of queries =======================================================

        # Inserts the country if it's not in the database
        if(self.curs.execute(checkCountry, (astro.country,)).fetchone() == None):
            self.curs.execute(insertCountry, (astro.country,))

        # Inserts the astronaut if they're not already in the database
        if(self.curs.execute(checkAstro, (astro.fName, astro.lName,)).fetchone() == None):
            # Convert the image to bytes for storage
            imgByteArr = io.BytesIO()
            astro.headshot.save(imgByteArr, format=astro.headshot.format)
            imgByteArr = imgByteArr.getvalue()

            # Execute query
            self.curs.execute(insertAstro, (astro.fName, astro.lName, astro.country, astro.facialData, imgByteArr,))
        else:
            print("{0} {1} is already in the database".format(astro.fName, astro.lName))

        if commit: self.conn.commit()

    def insert_astro_list(self, astroList):
        '''
        DESC:   Inserts a list of astronauts into the database

        INPUT:  astroList
        - A list of Astronaut objects

        OUTPUT: None
        '''

        for astro in astroList:
            insert_astro(astro, commit = False)

        self.conn.commit()

    def get_headshot(self, astro: Astronaut, save: bool = True, ret: bool = False):
        '''
        DESC:   Gets an astronaut's headshot from the database

        INPUT:  astro: Astronaut
        - An Astronaut object

        save: bool = True
        - Whether the file should be saved to the class instance

        ret: bool = True
        - Whether the file should be returned from the function

        OUTPUT: Will return an image if 'ret' is true
        '''

        # SQL queries ==========================================================
        getAstro = '''select Headshot from Astros where F_Name like ? and L_Name like ?;'''
        # End of queries =======================================================

        # Get the headshot from the database
        res = self.curs.execute(getAstro, (astro.fName, astro.lName,)).fetchone()
        if(res == None):
            print("{0} {1} is not in the database".format(astro.fName, astro.lName))
            return None

        # Convert the image back from bytes
        stream = io.BytesIO(res[0])
        image = Image.open(stream).convert("RGBA")
        stream.close()

        # Logic for saving/returning
        if save: astro.headshot = image
        if ret: return image

    def update_facial_data(self, astro: Astronaut, commit: bool = True):
        '''
        DESC:   Pushes an astronaut's facial data to the database

        INPUT:  astro: Astronaut
        - An astronaut object

        commit: bool = True
        - Whether the update should be commited or not. It should be
        commited any time you want to save data. However, this can
        take up time, and for a group of inserts, it can be left out
        until the last insert.

        OUTPUT: None
        '''

        # SQL queries ==========================================================
        updateAstro = '''update Astros
        set Facial_Encoding = ?
        where F_Name like ? and L_Name like ?;'''

        checkAstro = '''select * from Astros where F_Name like ? and L_Name like ?;'''
        # End of queries =======================================================

        # Checks to see if the astronaut is in the databse
        if(self.curs.execute(checkAstro, (astro.fName, astro.lName,)).fetchone() == None):
            print("{0} {1} is not in the database".format(astro.fName, astro.lName))
        else:
            # Convert the data to an appropriate storage format
            fd = astro.facialData.tobytes()
            self.curs.execute(updateAstro, (fd, astro.fName, astro.lName,))

            if commit: self.conn.commit()

    def update_facial_data_list(self, astroList):
        '''
        DESC:   Updates the facial data for all astronauts in a list

        INPUT:  astroList
        - A list of astronauts

        OUTPUT: None
        '''

        for astro in astroList:
            update_facial_data(astro, commit = False)

        self.conn.commit()

    def get_astros_from_database(self):
        '''
        DESC:   Pulls all of the astronauts from the database

        INPUT:  None

        OUTPUT: A list of astronauts
        '''

        # SQL queries ==========================================================
        getAstros = '''select Country, F_Name, L_Name, Facial_Encoding
        from Astros;'''
        # End of queries =======================================================

        # Execute query
        res = self.curs.execute(getAstros).fetchall()

        # Exit if there were no results
        if(res == None):
            print("There were no astronauts in the database")
            return None

        astros = []
        for r in res:
            # Converts the facial data from binary data if it exists
            if r[3] is not None: fd = np.frombuffer(r[3])
            else: fd = None

            astros.append(Astronaut(r[0], r[1], r[2], fData=fd))

        return astros


if __name__ == '__main__':
    a = Astro_Handler('Astro.sqlite')
