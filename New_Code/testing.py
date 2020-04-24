import Initialize_Db as idb
from PIL import Image
from Astro import Astronaut
import numpy as np

conn, c = idb.connect('Astro.sqlite')

# astro_im = Image.open("test.jpg")
astro = Astronaut('usa', 'matt', 'raymond')
# idb.insert_astro(conn, c, astro, astro_im)
astro.facialData = np.array([1.0, 2.0, 3.0, 4.0])
idb.update_facial_data(conn, c, astro)

# lst = [[Astronaut('usa', 'james', 'cameron'),astro_im],
#        [Astronaut('rus', 'bill', 'deblasio'),astro_im]]
# idb.insert_astro_list(conn, c, lst)

# astro_im = idb.get_headshot(c, astro.fName, astro.lName);
for k in idb.get_astros_from_database(c):
    print(k.facialData)
# astro_im.show()

idb.disconnect(conn)
