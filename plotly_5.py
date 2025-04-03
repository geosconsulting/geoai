import plotly.express as px

# Sample Data
df = px.data.tips()  # Replace with your own lat/lon data

# Create heatmap
fig = px.density_map(df, lat="total_bill", lon="tip",  # Replace with lat/lon fields
                         radius=10, map_style="stamen-terrain")

fig.show()
