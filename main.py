import xarray as xr
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI()

# Habilitar CORS para que pueda ser accedido desde otros orígenes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/wind")
def get_wind_data():
    # Ruta al archivo descargado
    archivo = Path("gfs_data/gfs.t12z.atmf000.nc")

    # Abre el archivo usando xarray
    ds = xr.open_dataset(archivo)

    # Extrae los datos de viento en el nivel más bajo (cercano a la superficie)
    u = ds['ugrd'].isel(time=0, pfull=-1)
    v = ds['vgrd'].isel(time=0, pfull=-1)
    lons = ds['lon'].values
    lats = ds['lat'].values

    # Convierte los valores a arrays de numpy
    u_vals = u.values
    v_vals = v.values

    # Lista para almacenar los datos en formato GeoJSON
    features = []

    step = 20  # menos puntos para simplificar la visualización
    for i in range(0, lats.shape[0], step):
        for j in range(0, lats.shape[1], step):
            lon = float(lons[i][j])
            lat = float(lats[i][j])
            u_val = float(u_vals[i][j])
            v_val = float(v_vals[i][j])
            speed = np.sqrt(u_val**2 + v_val**2)  # Velocidad del viento
            direction = np.arctan2(v_val, u_val) * 180 / np.pi  # Dirección del viento

            # Agrega el punto al GeoJSON
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "u": u_val,
                    "v": v_val,
                    "speed": speed,
                    "direction": direction
                }
            })

    # Retorna el GeoJSON con la información de los vientos
    return {
        "type": "FeatureCollection",
        "features": features
    }
