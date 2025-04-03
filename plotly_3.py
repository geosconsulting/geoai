import plotly.express as px

# Sample Data
df = px.data.carshare()

# Create a map
fig = px.scatter_map(df, lat="centroid_lat", lon="centroid_lon", size="car_hours")

fig.show()
