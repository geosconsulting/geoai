import pandas as pd
import folium
import random
from shapely.geometry import Point
import geopandas as gpd

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

# Creazione della mappa
mappa = folium.Map(location=[45.1, 9.1], zoom_start=12)

# Aggiunta UP
for _, row in df_up.iterrows():
    folium.Marker(
        location=[row['lat'], row['lon']],
        popup=f"{row['id']} - Produzione: {row['produzione_totale']}",
        icon=folium.Icon(color="blue", icon="envelope")
    ).add_to(mappa)

# Aggiunta LIS
for _, row in df_lis.iterrows():
    folium.Marker(
        location=[row['lat'], row['lon']],
        popup=f"{row['id']}",
        icon=folium.Icon(color="green", icon="shopping-cart")
    ).add_to(mappa)

# Aggiunta Banche
for _, row in df_banche.iterrows():
    folium.Marker(
        location=[row['lat'], row['lon']],
        popup=f"{row['id']} - {row['gruppo_bancario']}",
        icon=folium.Icon(color="red", icon="usd")
    ).add_to(mappa)

# Salvataggio mappa
mappa.save("mappa_simulazione.html")
mappa
