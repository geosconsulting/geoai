import plotly.express as px

# Sample Data (Iris dataset)
df = px.data.iris()

# Scatter plot
fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species")

# Show the plot
fig.show()