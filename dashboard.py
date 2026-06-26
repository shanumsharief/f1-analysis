import fastf1
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, State
import numpy as np
from scipy.interpolate import interp1d

fastf1.Cache.enable_cache('cache')

TEAL = '#00D2BE'
SILVER = '#FFFFFF'
BG = '#0a0a0a'
CARD = '#111111'
BORDER = '#222222'
TEXT = '#e8e8e8'
MUTED = '#666666'

# Available seasons
SEASONS = list(range(2018, 2025))

# Session types
SESSION_TYPES = [
    {'label': 'Qualifying', 'value': 'Q'},
    {'label': 'Race', 'value': 'R'},
    {'label': 'Sprint', 'value': 'S'},
]

def get_race_schedule(year):
    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        return [{'label': row['EventName'], 'value': row['EventName']}
                for _, row in schedule.iterrows()]
    except:
        return []

app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.index_string = '''
<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>F1 Analysis Dashboard</title>
    {%favicon%}
    {%css%}
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #0a0a0a; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0a0a0a; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
        .dark-dropdown .Select-control { background-color: #1a1a1a !important; border: 0.5px solid #333 !important; }
        .dark-dropdown .Select-value-label { color: #e8e8e8 !important; }
        .dark-dropdown .Select-single-value { color: #e8e8e8 !important; }
        .dark-dropdown .Select-menu-outer { background-color: #1a1a1a !important; border-color: #333 !important; }
        .dark-dropdown .Select-option { color: #e8e8e8 !important; background-color: #1a1a1a !important; }
        .dark-dropdown .Select-option.is-focused { background-color: #222 !important; }
        .dark-dropdown .Select-option.is-selected { background-color: #00D2BE22 !important; color: #00D2BE !important; }
        .dark-dropdown .Select-arrow { border-top-color: #666 !important; }
        .dark-dropdown input { background-color: #1a1a1a !important; color: #e8e8e8 !important; }
        .dark-dropdown .Select-placeholder { color: #666 !important; }
        ._dash-loading { color: #00D2BE !important; }
    </style>
</head>
<body>
    {%app_entry%}
    <footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </footer>
</body>
</html>
'''

def selector_card(label, color, child):
    return html.Div(style={
        'background': CARD, 'border': f'0.5px solid {BORDER}',
        'borderRadius': '8px', 'padding': '12px 16px', 'flex': '1'
    }, children=[
        html.Div(label, style={
            'fontSize': '10px', 'color': color,
            'letterSpacing': '1.2px', 'marginBottom': '8px', 'fontWeight': '500'
        }),
        child
    ])

def make_dropdown(id, options, value):
    return dcc.Dropdown(
        id=id, options=options, value=value,
        clearable=False, className='dark-dropdown',
        style={'backgroundColor': '#1a1a1a', 'color': TEXT, 'border': 'none'}
    )

app.layout = html.Div(style={
    'backgroundColor': BG, 'minHeight': '100vh',
    'padding': '28px 32px',
    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
}, children=[

    # Header
    html.Div(style={
        'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center',
        'borderBottom': f'0.5px solid {BORDER}', 'paddingBottom': '20px', 'marginBottom': '24px'
    }, children=[
        html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '12px'}, children=[
            html.Div(style={'width': '10px', 'height': '10px', 'borderRadius': '50%', 'backgroundColor': TEAL}),
            html.Div([
                html.Div("F1 Analysis Dashboard", style={'color': TEXT, 'fontSize': '16px', 'fontWeight': '500'}),
                html.Div(id='session-label', style={'color': MUTED, 'fontSize': '12px', 'marginTop': '2px'})
            ])
        ]),
        html.Span("FastF1 · Real telemetry data", style={
            'fontSize': '11px', 'color': MUTED,
            'border': f'0.5px solid {BORDER}', 'padding': '4px 12px', 'borderRadius': '20px'
        })
    ]),

    # Session selectors row
    html.Div(style={'display': 'flex', 'gap': '12px', 'marginBottom': '16px'}, children=[
        selector_card("SEASON", TEAL, make_dropdown(
            'season',
            [{'label': str(y), 'value': y} for y in SEASONS],
            2023
        )),
        selector_card("RACE", MUTED, make_dropdown('race', [], 'Monaco Grand Prix')),
        selector_card("SESSION", MUTED, make_dropdown('session-type', SESSION_TYPES, 'Q')),
    ]),

    # Driver selectors row
    html.Div(style={'display': 'flex', 'gap': '12px', 'marginBottom': '20px'}, children=[
        selector_card("DRIVER 1", TEAL, make_dropdown('driver1', [], 'VER')),
        selector_card("DRIVER 2", SILVER, make_dropdown('driver2', [], 'HAM')),
    ]),

    # Loading wrapper
    dcc.Loading(
        id='loading',
        type='circle',
        color=TEAL,
        children=[
            # Metric cards
            html.Div(id='metric-cards', style={
                'display': 'grid', 'gridTemplateColumns': 'repeat(4, 1fr)',
                'gap': '10px', 'marginBottom': '20px'
            }),

            # Telemetry chart
            html.Div(style={
                'background': CARD, 'border': f'0.5px solid {BORDER}',
                'borderRadius': '12px', 'padding': '4px', 'marginBottom': '12px'
            }, children=[dcc.Graph(id='telemetry-chart', config={'displayModeBar': False})]),

            # Delta chart
            html.Div(style={
                'background': CARD, 'border': f'0.5px solid {BORDER}',
                'borderRadius': '12px', 'padding': '4px'
            }, children=[dcc.Graph(id='delta-chart', config={'displayModeBar': False})]),
        ]
    ),

    # Hidden store for session data state
    dcc.Store(id='session-store'),
])


# Update race list when season changes
@app.callback(
    Output('race', 'options'),
    Output('race', 'value'),
    Input('season', 'value')
)
def update_races(year):
    races = get_race_schedule(year)
    default = races[4]['value'] if len(races) > 4 else races[0]['value']
    return races, default


# Update drivers when session changes
@app.callback(
    Output('driver1', 'options'),
    Output('driver2', 'options'),
    Output('driver1', 'value'),
    Output('driver2', 'value'),
    Output('session-store', 'data'),
    Input('race', 'value'),
    Input('season', 'value'),
    Input('session-type', 'value'),
    prevent_initial_call=True
)
def update_drivers(race, year, session_type):
    if not race:
        return [], [], None, None, None
    try:
        session = fastf1.get_session(year, race, session_type)
        session.load()
        drivers = sorted(session.laps['Driver'].unique().tolist())
        opts = [{'label': d, 'value': d} for d in drivers]
        d1 = 'VER' if 'VER' in drivers else drivers[0]
        d2 = 'HAM' if 'HAM' in drivers else drivers[1]
        return opts, opts, d1, d2, {'year': year, 'race': race, 'session_type': session_type}
    except Exception as e:
        print(f"Error loading session: {e}")
        return [], [], None, None, None


def make_metric_card(label, value, sub, color=TEXT):
    return html.Div(style={
        'background': CARD, 'border': f'0.5px solid {BORDER}',
        'borderRadius': '8px', 'padding': '14px 16px'
    }, children=[
        html.Div(label, style={'fontSize': '10px', 'color': MUTED, 'letterSpacing': '1px', 'marginBottom': '6px'}),
        html.Div(value, style={'fontSize': '20px', 'fontWeight': '500', 'color': color}),
        html.Div(sub, style={'fontSize': '11px', 'color': MUTED, 'marginTop': '4px'})
    ])


@app.callback(
    Output('telemetry-chart', 'figure'),
    Output('delta-chart', 'figure'),
    Output('metric-cards', 'children'),
    Output('session-label', 'children'),
    Input('driver1', 'value'),
    Input('driver2', 'value'),
    State('season', 'value'),
    State('race', 'value'),
    State('session-type', 'value'),
    prevent_initial_call=True
)
def update_charts(driver1, driver2, year, race, session_type):
    if not all([driver1, driver2, year, race, session_type]):
        empty = go.Figure()
        empty.update_layout(paper_bgcolor=CARD, plot_bgcolor=CARD, font=dict(color=TEXT))
        return empty, empty, [], ''

    try:
        session = fastf1.get_session(year, race, session_type)
        session.load()

        d1_lap = session.laps.pick_drivers(driver1).pick_fastest()
        d2_lap = session.laps.pick_drivers(driver2).pick_fastest()
        d1_tel = d1_lap.get_telemetry().add_distance()
        d2_tel = d2_lap.get_telemetry().add_distance()

        d1_laptime = d1_lap['LapTime'].total_seconds()
        d2_laptime = d2_lap['LapTime'].total_seconds()

        def fmt_time(secs):
            m = int(secs // 60)
            s = secs % 60
            return f"{m}:{s:06.3f}"

        gap = abs(d1_laptime - d2_laptime)
        faster = driver1 if d1_laptime < d2_laptime else driver2
        d1_top = d1_tel['Speed'].max()
        d2_top = d2_tel['Speed'].max()

        session_name = {'Q': 'Qualifying', 'R': 'Race', 'S': 'Sprint'}.get(session_type, session_type)
        label = f"{race} · {year} {session_name}"

        cards = [
            make_metric_card(f"{driver1} LAP TIME", fmt_time(d1_laptime), "fastest lap", TEAL),
            make_metric_card(f"{driver2} LAP TIME", fmt_time(d2_laptime), "fastest lap", SILVER),
            make_metric_card("GAP", f"+{gap:.3f}s", f"{faster} advantage", TEXT),
            make_metric_card("TOP SPEED", f"{max(d1_top, d2_top):.0f} km/h", f"{driver1} {d1_top:.0f} · {driver2} {d2_top:.0f}", TEXT),
        ]

        fig = make_subplots(
            rows=4, cols=1, shared_xaxes=True,
            row_heights=[0.35, 0.25, 0.2, 0.2],
            vertical_spacing=0.06
        )

        traces = [
            ('Speed', 'Speed (km/h)', 1),
            ('Throttle', 'Throttle %', 2),
            ('Brake', 'Brake', 3),
            ('nGear', 'Gear', 4),
        ]

        for col, label_text, row in traces:
            for tel, driver, color in [(d1_tel, driver1, TEAL), (d2_tel, driver2, SILVER)]:
                width = 1.5 if driver == driver1 else 2
                fig.add_trace(go.Scatter(
                    x=tel['Distance'], y=tel[col],
                    name=driver, line=dict(color=color, width=width),
                    legendgroup=driver, showlegend=(row == 1),
                    hovertemplate=f'<b>{driver}</b><br>{label_text}: %{{y:.1f}}<br>Distance: %{{x:.0f}}m<extra></extra>'
                ), row=row, col=1)
            fig.update_yaxes(
                title_text=label_text, row=row, col=1,
                title_font=dict(size=10, color=MUTED),
                tickfont=dict(size=10, color=MUTED),
                gridcolor='#1a1a1a', zerolinecolor='#1a1a1a'
            )

        fig.update_layout(
            paper_bgcolor=CARD, plot_bgcolor=CARD,
            font=dict(color=TEXT), height=580,
            margin=dict(l=60, r=20, t=40, b=40),
            legend=dict(orientation='h', y=1.02, x=1, xanchor='right',
                        font=dict(size=11, color=TEXT), bgcolor='rgba(0,0,0,0)'),
            title=dict(text=f'{driver1}  vs  {driver2}  —  Telemetry',
                       font=dict(size=13, color=MUTED), x=0.01),
        )
        fig.update_xaxes(gridcolor='#1a1a1a', zerolinecolor='#1a1a1a',
                         tickfont=dict(size=10, color=MUTED))

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
            fill='tozeroy', fillcolor='rgba(0, 210, 190, 0.12)',
            line=dict(color=TEAL, width=1.5),
            hovertemplate='Distance: %{x:.0f}m<br>Delta: %{y:.3f}s<extra></extra>'
        ))
        fig2.add_hline(y=0, line_dash='dot', line_color=BORDER, line_width=1)
        fig2.update_layout(
            paper_bgcolor=CARD, plot_bgcolor=CARD,
            font=dict(color=TEXT), height=220,
            margin=dict(l=60, r=20, t=40, b=40),
            showlegend=False,
            title=dict(text=f'Lap delta  —  positive = {driver1} faster',
                       font=dict(size=13, color=MUTED), x=0.01),
            xaxis=dict(title='Distance (m)', gridcolor='#1a1a1a',
                       tickfont=dict(size=10, color=MUTED),
                       title_font=dict(size=10, color=MUTED)),
            yaxis=dict(title='Delta (s)', gridcolor='#1a1a1a',
                       tickfont=dict(size=10, color=MUTED),
                       title_font=dict(size=10, color=MUTED))
        )

        return fig, fig2, cards, label

    except Exception as e:
        print(f"Error: {e}")
        empty = go.Figure()
        empty.update_layout(paper_bgcolor=CARD, plot_bgcolor=CARD, font=dict(color=TEXT))
        return empty, empty, [], 'Error loading session'


if __name__ == '__main__':
    app.run(debug=False)