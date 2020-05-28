from sqlite3 import Connection, Cursor
import sqlite3
from PIL import Image
from Astro import Astronaut
import io
import numpy as np
import os
from DB_Handler import Astro_Handler


ah = Astro_Handler('Astro.sqlite')

a = Astronaut('usa', 'matt', 'raymond')
print(a)

ah.get_headshot(a)
print(a)
