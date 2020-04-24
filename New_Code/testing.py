import Initialize_Db as idb
from PIL import Image
from Astro import Astronaut

conn, c = idb.connect('Astro.sqlite')

astro_im = Image.open("test.jpg")
astro = Astronaut('usa', 'bill', 'nye')
idb.insert_astro(conn, c, astro, astro_im)

astro_im = idb.get_headshot(c, astro.fName, astro.lName);
astro_im.show()

idb.disconnect(conn)
