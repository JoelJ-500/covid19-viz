import os
import pandas as pd
from flask import Flask, render_template, request
import plotly.express as px
import plotly.offline as opy

app = Flask(__name__)

# Find the absolute path to your app.py folder, then join it with the CSV filename
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "COVID_Cleaned.csv")

# Load processed data safely using the absolute path
df = pd.read_csv(csv_path, parse_dates=["date"])

@app.route('/')
def index():
    # Load data
    countries = sorted(df['country'].unique().tolist())
    min_date = df['date'].min().strftime('%Y-%m-%d')
    max_date = df['date'].max().strftime('%Y-%m-%d')
    summary = {
        "countries": countries,
        "date_range": f"{min_date} to {max_date}",
        "total_records": len(df)
    }

    selected_country = countries[0]
    selected_metric = 'new_cases'

    # Filter data for initial plot
    filtered_df = df[df['country'] == selected_country].sort_values('date')
    
    fig = px.line(
        filtered_df, 
        x='date', 
        y=selected_metric,
        title=f"{selected_metric.replace('_', ' ').title()} in {selected_country}",
        labels={'date': 'Date', selected_metric: selected_metric.replace('_', ' ').title()},
        template='plotly_dark'
    )
    import plotly.io as pio
    graph_json = pio.to_json(fig)

    return render_template(
        'index.html', 
        summary=summary, 
        graph_json=graph_json, 
        selected_country=selected_country,
        selected_metric=selected_metric
    )

@app.route('/data')
def get_data():
    country = request.args.get('country')
    metric = request.args.get('metric')
    
    # Filter data
    filtered_df = df[df['country'] == country].sort_values('date')
    
    # Select columns and convert to dict
    # We include 'date' (converted to string) and the chosen metric
    data = {
        "x": filtered_df['date'].dt.strftime('%Y-%m-%d').tolist(),
        "y": filtered_df[metric].tolist(),
        "title": f"{metric.replace('_', ' ').title()} in {country}"
    }
    return data

if __name__ == '__main__':
    app.run(debug=True, port=5000)
