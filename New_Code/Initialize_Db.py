import sqlite3

# SQL queries
create_astros = '''create table if not exists Astros (
    ID int autoincriment not null,
    F_Name varchar(32) not null,
    M_Name varchar(32) default null,
    L_Name varchar(32) not null,
    Headshot blob default null,
    Facial_Encoding blob default null,
    primary key (ID)
);'''

create_photos = '''create table if not exists Photos (
    File_Name varchar(128) not null,
    primary key (File_Name)
);'''

create_links = '''create table if not exists Photo_Link (
    Photo_ID int not null,
    Astro_ID int not null,
    primary key (Photo_ID, Astro_ID),
    foreign key (Photo_ID) references Photos,
    foreign key (Astro_ID) references Astros
);'''

def create_database(con_string):
    queries = [create_astros, create_photos, create_links]

    conn = sqlite3.connect(con_string)
    c = conn.cursor()

    for q in queries:
        c.execute(q)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_database('Astro.sqlite')
