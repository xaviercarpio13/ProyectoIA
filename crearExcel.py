import pandas as pd


def crearBD (songs_info):
  # lista de datos de Spotify-Peruano
  datos = []
  for cancion in songs_info:
    datos.append(cancion)

  # Crear DataFrame
  df = pd.DataFrame(datos)

  # Guardar como archivo CSV
  nombre_csv = 'datos_spotify.csv'
  df.to_csv(nombre_csv, index=False)
  print(f'Se ha generado el archivo CSV: {nombre_csv}')

  # Guardar como archivo Excel
  nombre_excel = 'datos_spotify.xlsx'
  df.to_excel(nombre_excel, index=False)
  print(f'Se ha generado el archivo Excel: {nombre_excel}')

  return None