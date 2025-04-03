import plotly.graph_objects as go

# Create figure
fig = go.Figure()

# Add a scatter plot
fig.add_trace(go.Scatter(x=[1, 2, 3], y=[3, 1, 6], mode="lines+markers", name="Example Line"))

# Customize layout
fig.update_layout(title="Custom Plot", xaxis_title="X Axis", yaxis_title="Y Axis")

# Show the plot
fig.show()
