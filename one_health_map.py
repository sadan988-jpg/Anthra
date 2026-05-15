import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import sqlite3
import os

# Initialize the Dash app
app = dash.Dash(__name__)

def get_data():
    # Fetch Animal Risk Data
    with sqlite3.connect('healthcare.db') as conn:
        df_animal = pd.read_sql_query("SELECT district, pincode, pathogen_type, risk_level, 'Animal' as type FROM animal_disease_risks", conn)
        df_human = pd.read_sql_query("SELECT pincode, risk_level as risk, 'Human' as type FROM outbreak_predictions", conn)
    
    # Convert categorical human risk to numerical for plotting size
    risk_map = {"Low": 0.2, "Medium": 0.6, "High": 1.0}
    df_human['risk_num'] = df_human['risk'].map(lambda x: risk_map.get(x, 0.1))
    
    # Mock coordinates for Karnataka districts (for demo map)
    coords = {
        "Bengaluru Urban": [12.9716, 77.5946],
        "Bengaluru Rural": [13.2307, 77.7126],
        "Mysuru": [12.2958, 76.6394],
        "Shivamogga": [13.9299, 75.5681],
        "Belagavi": [15.8497, 74.4977]
    }
    
    df_animal['lat'] = df_animal['district'].map(lambda x: coords.get(x, [12.9, 77.5])[0])
    df_animal['lon'] = df_animal['district'].map(lambda x: coords.get(x, [12.9, 77.5])[1])
    
    # Map pincodes to coordinates for human clusters
    df_human['lat'] = df_human['pincode'].map(lambda x: 12.9716 + (random.uniform(-0.05, 0.05)))
    df_human['lon'] = df_human['pincode'].map(lambda x: 77.5946 + (random.uniform(-0.05, 0.05)))
    
    return df_animal, df_human

app.layout = html.Div([
    html.H1("One Health Sentinel: Zoonotic Overlap Map", style={'textAlign': 'center', 'color': '#fff'}),
    html.P("Correlating NADRES v2 Animal Alerts with Real-time Human Symptom Clusters", style={'textAlign': 'center', 'color': '#888'}),
    
    dcc.Graph(id='spillover-map', style={'height': '700px'}),
    
    dcc.Interval(id='interval-component', interval=10*1000, n_intervals=0),
    
    html.Div([
        html.Div([
            html.H3("Animal Risk Districts (Color: Red)", style={'color': '#ef4444'}),
            html.P("Source: ICAR-NIVEDI NADRES v2")
        ], style={'width': '45%', 'display': 'inline-block', 'padding': '20px'}),
        
        html.Div([
            html.H3("Human Symptom Clusters (Color: Blue)", style={'color': '#3b82f6'}),
            html.P("Source: SecurePredict AI Diagnostics")
        ], style={'width': '45%', 'display': 'inline-block', 'padding': '20px'})
    ], style={'background': '#111', 'borderRadius': '10px', 'marginTop': '20px'})
], style={'backgroundColor': '#000', 'padding': '40px', 'fontFamily': 'Inter, sans-serif'})

import random

@app.callback(Output('spillover-map', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph(n):
    df_a, df_h = get_data()
    
    fig = px.scatter_mapbox(df_a, lat="lat", lon="lon", size="risk_level", color_discrete_sequence=['#ef4444'],
                            hover_name="district", hover_data=["pathogen_type", "risk_level"],
                            zoom=6, height=700)
    
    fig2 = px.scatter_mapbox(df_h, lat="lat", lon="lon", size="risk_num", color_discrete_sequence=['#3b82f6'],
                             hover_name="pincode", zoom=6)
    
    fig.add_trace(fig2.data[0])
    
    fig.update_layout(
        mapbox_style="carto-darkmatter",
        margin={"r":0,"t":0,"l":0,"b":0},
        paper_bgcolor="#000",
        plot_bgcolor="#000",
        showlegend=False
    )
    
    return fig

if __name__ == '__main__':
    app.run(debug=True, port=8050)
