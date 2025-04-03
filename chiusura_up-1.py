import pandas as pd
import folium
import random
from shapely.geometry import Point, Polygon
import geopandas as gpd
from scipy.spatial import distance
import matplotlib.pyplot as plt
import numpy as np

# Generazione dati fittizi per UP (Uffici Postali)
n_up = 10
up_data = {
    "id": [f"UP_{i}" for i in range(n_up)],
    "lat": [random.uniform(45.0, 45.2) for _ in range(n_up)],
    "lon": [random.uniform(9.0, 9.2) for _ in range(n_up)],
    "produzione_totale": [random.randint(5000, 20000) for _ in range(n_up)],
    "bollettini": [random.randint(1000, 5000) for _ in range(n_up)],
    "pagoPA_MAV": [random.randint(500, 3000) for _ in range(n_up)],
    "ricariche_postepay": [random.randint(500, 2000) for _ in range(n_up)],
    "pacchi": [random.randint(300, 1500) for _ in range(n_up)],
}
df_up = pd.DataFrame(up_data)

# Generazione dati fittizi per LIS (punti vendita autorizzati)
n_lis = 15
lis_data = {
    "id": [f"LIS_{i}" for i in range(n_lis)],
    "lat": [random.uniform(45.0, 45.2) for _ in range(n_lis)],
    "lon": [random.uniform(9.0, 9.2) for _ in range(n_lis)],
    "abilitazione_bollettini": [random.choice([True, False]) for _ in range(n_lis)],
    "abilitazione_pagoPA_MAV": [random.choice([True, False]) for _ in range(n_lis)],
    "abilitazione_ricariche_postepay": [random.choice([True, False]) for _ in range(n_lis)],
    "abilitazione_pacchi": [random.choice([True, False]) for _ in range(n_lis)],
}
df_lis = pd.DataFrame(lis_data)

# Generazione dati fittizi per Banche
n_banche = 8
banche_data = {
    "id": [f"BANCA_{i}" for i in range(n_banche)],
    "lat": [random.uniform(45.0, 45.2) for _ in range(n_banche)],
    "lon": [random.uniform(9.0, 9.2) for _ in range(n_banche)],
    "gruppo_bancario": [random.choice(["Gruppo A", "Gruppo B", "Gruppo C"]) for _ in range(n_banche)],
    "peso_competitivo": [random.uniform(0.5, 1.5) for _ in range(n_banche)],
}
df_banche = pd.DataFrame(banche_data)

# Generazione dati fittizi sulla densità territoriale con poligoni
n_sezioni = 5
sezioni_data = []
for i in range(n_sezioni):
    center_lat, center_lon = random.uniform(45.0, 45.2), random.uniform(9.0, 9.2)
    polygon = Polygon([
        (center_lon + random.uniform(-0.01, 0.01), center_lat + random.uniform(-0.01, 0.01)) for _ in range(5)
    ])
    sezioni_data.append({
        "id": f"SEZ_{i}",
        "geometry": polygon,
        "densita": random.choice(["Alta", "Media", "Bassa"]),
        "popolazione": random.randint(500, 5000)
    })

gdf_sezioni = gpd.GeoDataFrame(sezioni_data, crs="EPSG:4326")

# Definizione dei bacini d'utenza in base alla densità territoriale
def get_bacino(densita):
    return {"Alta": 500, "Media": 1000, "Bassa": 3000}[densita]

df_up["bacino"] = df_up.apply(lambda row: get_bacino(random.choice(["Alta", "Media", "Bassa"])), axis=1)

# Creazione della mappa
mappa = folium.Map(location=[45.1, 9.1], zoom_start=12)

# Aggiunta sezioni con poligoni
for _, row in gdf_sezioni.iterrows():
    folium.GeoJson(
        row["geometry"].__geo_interface__,
        name=row["id"],
        style_function=lambda x: {
            "fillColor": "#ff7800" if row["densita"] == "Alta" else "#ffff00" if row["densita"] == "Media" else "#00ff00",
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.4
        }
    ).add_to(mappa)

# Analisi di intersezione tra UP e sezioni censuarie
gdf_up = gpd.GeoDataFrame(df_up, geometry=gpd.points_from_xy(df_up.lon, df_up.lat), crs="EPSG:4326")
gdf_up = gdf_up.to_crs(gdf_sezioni.crs)

gdf_up["sezioni_intersecate"] = gdf_up.geometry.apply(lambda x: [row.id for _, row in gdf_sezioni.iterrows() if row.geometry.contains(x)])
gdf_up["popolazione_coinvolta"] = gdf_up.geometry.apply(lambda x: sum(row.popolazione for _, row in gdf_sezioni.iterrows() if row.geometry.contains(x)))

# Aggiunta UP con bacini
for _, row in df_up.iterrows():
    folium.Circle(
        location=[row['lat'], row['lon']],
        radius=row["bacino"],
        color="blue",
        fill=True,
        fill_opacity=0.2
    ).add_to(mappa)
    folium.Marker(
        location=[row['lat'], row['lon']],
        popup=f"{row['id']} - Produzione: {row['produzione_totale']}\nBacino: {row['bacino']}m\nSezioni Intersecate: {', '.join(gdf_up.loc[gdf_up.id == row['id'], 'sezioni_intersecate'].values[0])}\nPopolazione Coinvolta: {gdf_up.loc[gdf_up.id == row['id'], 'popolazione_coinvolta'].values[0]}",
        icon=folium.Icon(color="blue", icon="envelope")
    ).add_to(mappa)

# Salvataggio mappa
mappa.save("mappa_simulazione-1.html")
mappa
