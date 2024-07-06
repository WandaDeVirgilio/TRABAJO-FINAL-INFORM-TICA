#https://colab.research.google.com/drive/182Q9SMP8A4OoeF3_YeYpg4nKZdO0FnTV?usp=sharing#scrollTo=lQWTLlgdRpgW 

import sqlite3
import pandas as pd

ruta_base = 'base1.db'
conexion = sqlite3.connect(ruta_base)
cursor = conexion.cursor()

cursor.execute("SELECT precio, servicios, nombre FROM profesionales")
data = cursor.fetchall()

columnas = ['precio', 'servicios', 'nombre']
df = pd.DataFrame(data, columns=columnas)
df.to_csv('profesionales.csv', index=False)

conexion.close()
