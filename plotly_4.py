import plotly.express as px
import json

# Load geojson (you need a valid GeoJSON file)
geojson_url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"

# Sample Data
df = px.data.election()  # Replace with your own geospatial data

# Create choropleth map
fig = px.choropleth(df, geojson=geojson_url, locations="district", color="winner",
                     featureidkey="properties.fips",
                     color_continuous_scale="Viridis",
                     title="Example Choropleth Map")

fig.update_geos(fitbounds="locations", visible=False)
fig.show()
