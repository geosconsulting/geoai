import plotly.express as px
import pandas as pd

def generate_plotly_insights(csv_file_path):
    """
    Generates interactive plots and insights from a CSV file using Plotly Express.

    Args:
        csv_file_path (str): The path to the CSV file.
    """
    try:
        df = pd.read_csv(csv_file_path)

        # Basic overview
        print("Data Overview:")
        print(df.head())
        print(df.info())
        print(df.describe())

        # Example visualizations (adapt based on your data)

        # 1. Scatter plot (numeric vs. numeric)
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) >= 2:
            fig_scatter = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], title=f"{numeric_cols[0]} vs {numeric_cols[1]}")
            fig_scatter.show()

        # 2. Histogram (distribution of a numeric column)
        if len(numeric_cols) >= 1:
            fig_hist = px.histogram(df, x=numeric_cols[0], title=f"Distribution of {numeric_cols[0]}")
            fig_hist.show()

        # 3. Bar chart (categorical vs. numeric)
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            fig_bar = px.bar(df, x=categorical_cols[0], y=numeric_cols[0], title=f"{numeric_cols[0]} by {categorical_cols[0]}")
            fig_bar.show()

        # 4. Box plot (categorical vs. numeric)
        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            fig_box = px.box(df, x=categorical_cols[0], y=numeric_cols[0], title=f"Box plot of {numeric_cols[0]} by {categorical_cols[0]}")
            fig_box.show()

        # 5. Line chart (time series, if applicable)
        # Check if there is a date column. If so, create a line chart.
        date_cols = df.select_dtypes(include=['datetime64', 'datetime64[ns]']).columns
        if len(date_cols) == 0:
            for col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col])
                    date_cols = [col]
                    break
                except (ValueError, TypeError):
                    pass
        if len(date_cols) >= 1 and len(numeric_cols) >= 1:
            fig_line = px.line(df, x=date_cols[0], y=numeric_cols[0], title=f"{numeric_cols[0]} over time")
            fig_line.show()

        # 6. Pie chart (categorical distribution)
        if len(categorical_cols) >= 1:
            fig_pie = px.pie(df, names=categorical_cols[0], title=f"Distribution of {categorical_cols[0]}")
            fig_pie.show()

        # 7. Heatmap (correlation matrix)
        if len(numeric_cols) >= 2:
            correlation_matrix = df[numeric_cols].corr()
            fig_heatmap = px.imshow(correlation_matrix, x=numeric_cols, y=numeric_cols, title="Correlation Matrix")
            fig_heatmap.show()

        # Add more visualizations as needed based on your data and goals.

    except FileNotFoundError:
        print(f"Error: File not found at {csv_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage (replace 'your_data.csv' with the actual path to your CSV file):
generate_plotly_insights('../analisi_negozio/cleaned_negozio.csv')