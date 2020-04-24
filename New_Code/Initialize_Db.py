from sqlite3 import Connection, Cursor
import sqlite3
from PIL import Image
from Astro import Astronaut
import io


def create_database(con_string):
    # SQL queries
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

    queries = [create_countries, create_astros, create_photos, create_links]

    conn = sqlite3.connect(con_string)
    c = conn.cursor()

    for q in queries:
        c.execute(q)

    conn.commit()
    conn.close()


def insert_astro(conn: Connection, curs: Cursor, astro: Astronaut, headshot: Image):
    checkCountry = '''select * from Countries where Abr_Name like ?;'''
    checkAstro = '''select * from Astros where F_Name like ? and L_Name like ?;'''

    insertAstro = '''insert into Astros (F_Name, L_Name, Country, Facial_Encoding, Headshot)
    values (?, ?, ?, ?, ?);
    '''

    insertCountry = '''insert into Countries (Abr_Name)
    values (?);
    '''

    if(curs.execute(checkCountry, (astro.country,)).fetchone() == None):
        curs.execute(insertCountry, (astro.country,))

    if(curs.execute(checkAstro, (astro.fName, astro.lName,)).fetchone() == None):
        imgByteArr = io.BytesIO()
        headshot.save(imgByteArr, format=headshot.format)
        imgByteArr = imgByteArr.getvalue()

        curs.execute(insertAstro, (astro.fName, astro.lName, astro.country, astro.facialData, imgByteArr,))
    else:
        print("{0} {1} is already in the database".format(astro.fName, astro.lName))

    conn.commit()


def get_headshot(curs: Cursor, fname: str, lname: str):
    getAstro = '''select Headshot from Astros where F_Name like ? and L_Name like ?;'''

    res = curs.execute(getAstro, (fname, lname,)).fetchone()
    if(res == None):
        print("{0} {1} is not in the database".format(fname, lname))
        return None

    stream = io.BytesIO(res[0])
    image = Image.open(stream).convert("RGBA")
    stream.close()
    return image


def connect(con_string: str):
    conn = sqlite3.connect(con_string)
    return conn, conn.cursor()


def disconnect(conn: Connection):
    conn.close()



if __name__ == '__main__':
    create_database('Astro.sqlite')
