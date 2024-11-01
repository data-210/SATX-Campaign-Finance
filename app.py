from dash import Dash, dash_table, dcc, html, Input, Output, State
import pandas as pd
from collections import OrderedDict
import dash_bootstrap_components as dbc

df = pd.read_csv('data/campaign_finance20241031.csv')

# Convert TransDate: to date time
df['TransDate:'] = pd.to_datetime(df['TransDate:'], errors='coerce')

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [html.H2("COSA Campaign Finance Data Dashboard",
                             style={'text-align': 'center'})]
                ),
                
            ]
        ),        
        dbc.Row(
            [
                dbc.Col(
                    html.H4("Total Contributions to Candidates & Committees",
                            style={'text-align': 'center',
                                   'marginTop': '40px', 
                                   'marginBottom': '15px'}),
                            width=12
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        options=[{'label': str(int(year)), 'value': int(year)} for year in df['Election Year'].dropna().unique()],
                        id='year-dropdown',
                        placeholder='Select Election Year',
                    ),
                    width=6
                ),
            ],
            style={'marginTop': '20px'}
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(id='cand-committee-graph')
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.H4("Contributions to Candidates Over Time", style={'text-align': 'center',
                                                                            'marginTop': '40px',
                                                                            'marginBottom': '15px'}),
                    width=12
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        options=[{'label': candidate, 'value': candidate} for candidate in df['Cand/Committee:'].unique()],
                        id='candidate-dropdown',
                        multi=True,
                        placeholder='Select Candidate(s)',
                    ),
                    width=6
                ),
                dbc.Col(
                            dcc.Dropdown(
                                options=[{'label': str(int(year)), 'value': int(year)} for year in df['Election Year'].dropna().unique()],
                                id='year-dropdown-ts',
                                placeholder='Select Election Year',
                            ),
                            width=6
                        ),
            ],
            style={'marginTop': '20px', 'marginBottom': '10px'}
        ),
        
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(id='timeseries-graph')
                )
            ]
        ),
        dbc.Container(
            [
                # Header
                dbc.Row(
                    [
                        dbc.Col(
                            html.H4(
                                "Download COSA Campaign Finance Data",
                                style={'text-align': 'center', 'marginTop': '20px', 'marginBottom': '10px'}
                            ),
                            width=12
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Dropdown(
                                options=[
                                    {'label': 'Excel file', 'value': 'excel'},
                                    {'label': 'CSV file', 'value': 'csv'},
                                ],
                                id='dropdown',
                                placeholder='Choose download file type. Default is CSV',
                            ),
                            width=3
                        ),
                        dbc.Col(
                            dbc.Button('Download data', id='btn-csv'),
                            width=3
                        ),
                    ],
                    style={'marginTop': '20px'}
                ),
                # Data table with extra margin at the bottom
                dbc.Row(
                    [
                        dbc.Col(
                            dash_table.DataTable(
                                id='datatable-interactivity',
                                data=df.to_dict('records'),
                                columns=[{'name': i, 'id': i} for i in df.columns],
                                page_size=25,
                                style_table={'overflowX': 'auto'},
                                filter_action='native',
                                sort_action='native',
                                column_selectable='single',
                                row_selectable='multi'
                            ),
                            width=12
                        ),
                        html.Div(id='datatable-interactivity-container')
                    ],
                    style={'marginTop': '20px', 'paddingBottom': '40px'}
                ),
            ],
            style={'paddingBottom': '40px', 'marginBottom': '20px'}
        ),
        dcc.Download(id='download'),
    ],
    style={'paddingBottom': '40px'}
)

               
# Callback for downloading data
@app.callback(
    Output('download', 'data'),
    Input('btn-csv', 'n_clicks'),
    State('dropdown', 'value'),
    prevent_initial_call=True,
)

def func(n_clicks_btn, download_type):
    if download_type == 'csv':
        return dcc.send_data_frame(df.to_csv, 'cosa_cf.csv')
    else:
        return dcc.send_data_frame(df.to_excel, 'cosa_cf.xlsx')

# Callback for updating candidate-based bar graph
@app.callback(
    Output('cand-committee-graph', 'figure'),
    Input('year-dropdown', 'value')
)
def update_graph(selected_year):
    filtered_df = df[df['Contact Type:'] == 'Contributor']
    if selected_year:
        filtered_df = filtered_df[filtered_df['Election Year'] == selected_year]

    agg_df = filtered_df.groupby('Cand/Committee:')['Amount:'].sum().reset_index()

    fig = {
        'data': [{
            'x': agg_df['Cand/Committee:'],
            'y': agg_df['Amount:'],
            'type': 'bar'
        }],
        'layout': {
            'title': f'Contributions to Candidate/Committee for {selected_year or "All Years"}',
            'xaxis': {'title': 'Candidate/Committee'},
            'yaxis': {'title': 'Total Contributions ($)'}
        }
    }
    return fig    

# Callback for timeseries chart
@app.callback(
    Output('timeseries-graph', 'figure'),
    [Input('year-dropdown-ts', 'value'), Input('candidate-dropdown', 'value')]
)
def update_timeseries(selected_year, selected_candidates):
    filtered_df = df[df['Contact Type:'] == 'Contributor']
    if selected_year:
        filtered_df = filtered_df[filtered_df['Election Year'] == selected_year]
    
    if selected_candidates:
        filtered_df = filtered_df[filtered_df['Cand/Committee:'].isin(selected_candidates)]
    
    # Aggregate data by Cand/Committee: and TransDate:
    timeseries_df = filtered_df.groupby(['TransDate:', 'Cand/Committee:'])['Amount:'].sum().reset_index()

    # Sort by date to ensure cumsums are in order
    timeseries_df = timeseries_df.sort_values(by=['Cand/Committee:', 'TransDate:'])

    # Calculate cumsum for each candidate
    timeseries_df['Cumulative Contributions'] = timeseries_df.groupby('Cand/Committee:')['Amount:'].cumsum()

    fig = {
        'data': [{
            'x': timeseries_df[timeseries_df['Cand/Committee:']==candidate]['TransDate:'],
            'y': timeseries_df[timeseries_df['Cand/Committee:']==candidate]['Cumulative Contributions'],
            'type': 'line',
            'name': candidate
        } for candidate in timeseries_df['Cand/Committee:'].unique()],
        'layout': {
            'title': 'Cumulative Contributions to Candidates Over Time',
            'xaxis': {'title': 'Date'},
            'yaxis': {'title': 'Cumulative Contributions ($)'},
            'showlegend': True
        }
    }
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)