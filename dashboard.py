import fastf1
import fastf1.plotting
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

fastf1.Cache.enable_cache('cache')

# Load session
session = fastf1.get_session(2023, 'Monaco', 'Q')
session.load()

# Get all driver codes
drivers = session.laps['Driver'].unique().tolist()

app = dash.Dash(__name__)

app.layout = html.Div(style={'backgroundColor': '#1a1a2e', 'minHeight': '100vh', 'padding': '20px', 'fontFamily': 'Arial'}, children=[

    html.H1("🏎️ F1 Race Analysis Dashboard",
            style={'color': '#e94560', 'textAlign': 'center', 'marginBottom': '5px'}),
    html.H3("Monaco 2023 Qualifying",
            style={'color': '#aaaaaa', 'textAlign': 'center', 'marginTop': '0px'}),

    # Driver selectors
    html.Div(style={'display': 'flex', 'justifyContent': 'center', 'gap': '40px', 'marginBottom': '20px'}, children=[
        html.Div([
            html.Label("Driver 1", style={'color': '#0600EF', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='driver1',
                options=[{'label': d, 'value': d} for d in drivers],
                value='VER',
                style={'width': '150px', 'backgroundColor': '#16213e', 'color': 'black'}
            )
        ]),
        html.Div([
            html.Label("Driver 2", style={'color': '#00D2BE', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='driver2',
                options=[{'label': d, 'value': d} for d in drivers],
                value='HAM',
                style={'width': '150px', 'backgroundColor': '#16213e', 'color': 'black'}
            )
        ]),
    ]),

    # Lap time display
    html.Div(id='lap-times', style={'textAlign': 'center', 'marginBottom': '20px'}),

    # Main telemetry chart
    dcc.Graph(id='telemetry-chart', style={'marginBottom': '20px'}),

    # Delta chart
    dcc.Graph(id='delta-chart'),
])


@app.callback(
    Output('telemetry-chart', 'figure'),
    Output('delta-chart', 'figure'),
    Output('lap-times', 'children'),
    Input('driver1', 'value'),
    Input('driver2', 'value')
)
def update_charts(driver1, driver2):
    # Get fastest laps
    d1_lap = session.laps.pick_drivers(driver1).pick_fastest()
    d2_lap = session.laps.pick_drivers(driver2).pick_fastest()

    d1_tel = d1_lap.get_telemetry().add_distance()
    d2_tel = d2_lap.get_telemetry().add_distance()

    d1_time = str(d1_lap['LapTime']).split()[-1][:11]
    d2_time = str(d2_lap['LapTime']).split()[-1][:11]

    # --- Telemetry figure ---
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                        subplot_titles=('Speed (km/h)', 'Throttle (%)', 'Brake', 'Gear'),
                        vertical_spacing=0.08)

    for tel, driver, color in [(d1_tel, driver1, '#0600EF'), (d2_tel, driver2, '#00D2BE')]:
        fig.add_trace(go.Scatter(x=tel['Distance'], y=tel['Speed'], name=driver, line=dict(color=color), legendgroup=driver), row=1, col=1)
        fig.add_trace(go.Scatter(x=tel['Distance'], y=tel['Throttle'], name=driver, line=dict(color=color), legendgroup=driver, showlegend=False), row=2, col=1)
        fig.add_trace(go.Scatter(x=tel['Distance'], y=tel['Brake'], name=driver, line=dict(color=color), legendgroup=driver, showlegend=False), row=3, col=1)
        fig.add_trace(go.Scatter(x=tel['Distance'], y=tel['nGear'], name=driver, line=dict(color=color), legendgroup=driver, showlegend=False), row=4, col=1)

    fig.update_layout(
        paper_bgcolor='#1a1a2e',
        plot_bgcolor='#16213e',
        font=dict(color='white'),
        height=700,
        title=dict(text=f'{driver1} vs {driver2} — Telemetry', font=dict(color='white')),
        legend=dict(font=dict(color='white'))
    )
    fig.update_xaxes(gridcolor='#333355')
    fig.update_yaxes(gridcolor='#333355')

    # --- Delta figure ---
    d1_dist = d1_tel['Distance'].values
    d1_t = d1_tel['Time'].dt.total_seconds().values
    d2_dist = d2_tel['Distance'].values
    d2_t = d2_tel['Time'].dt.total_seconds().values

    common_dist = np.linspace(0, min(d1_dist[-1], d2_dist[-1]), 1000)
    d1_interp = interp1d(d1_dist, d1_t)(common_dist)
    d2_interp = interp1d(d2_dist, d2_t)(common_dist)
    delta = d2_interp - d1_interp

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=common_dist, y=delta,
        fill='tozeroy',
        line=dict(color='#e94560'),
        name='Delta'
    ))
    fig2.add_hline(y=0, line_dash='dash', line_color='white', opacity=0.5)
    fig2.update_layout(
        paper_bgcolor='#1a1a2e',
        plot_bgcolor='#16213e',
        font=dict(color='white'),
        height=300,
        title=dict(text=f'Lap Delta — positive = {driver1} faster', font=dict(color='white')),
        xaxis_title='Distance (m)',
        yaxis_title='Delta (s)'
    )
    fig2.update_xaxes(gridcolor='#333355')
    fig2.update_yaxes(gridcolor='#333355')

    # Lap time display
    lap_display = html.Div([
        html.Span(f"{driver1}: {d1_time}", style={'color': '#0600EF', 'fontWeight': 'bold', 'fontSize': '18px', 'marginRight': '40px'}),
        html.Span(f"{driver2}: {d2_time}", style={'color': '#00D2BE', 'fontWeight': 'bold', 'fontSize': '18px'})
    ])

    return fig, fig2, lap_display


if __name__ == '__main__':
    app.run(debug=True)