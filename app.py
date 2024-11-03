from dash import Dash, dash_table, dcc, html, Input, Output, State
import pandas as pd
from collections import OrderedDict
import dash_bootstrap_components as dbc

df = pd.read_csv('data/campaign_finance20241031.csv')

# Convert TransDate: to date time
df['TransDate:'] = pd.to_datetime(df['TransDate:'], errors='coerce')
# Add last transaction date and date last downloaded
last_transaction_date = df['TransDate:'].max().strftime('%m/%d/%Y')
data_last_download = '10/31/2024'

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.Div(f"Data Last Downloaded: {data_last_download}"),
                            html.Div(f"Date of Last Transaction: {last_transaction_date}")
                        ],
                        style={'text-align': 'right', 'fontSize': '16px', 'color': 'gray'}
                    ),
                    width=12
                ),
            ],
            style={'marginBottom': '10px'}
        ),
         dbc.Row(
            [
                dbc.Col(
                    html.H2("COSA Campaign Finance Data"),
                    width=12,
                    style={'text-align': 'center'}
                )
            ],
            justify="center",
            align='center',
            style={'marginBottom': '20px'}
        ),      
        dbc.Row(
            [
                dbc.Col(
                    html.H4("Total Monetary Political Contributions to Candidates & Committees",
                            style={'text-align': 'center',
                                   'marginTop': '40px', 
                                   'marginBottom': '15px'}),
                            width=12
                ),
                dbc.Col(
                    dcc.Dropdown(
                        options=[{'label': str(int(year)), 'value': int(year)} for year in df['Election Year'].dropna().unique()],
                        id='year-dropdown',
                        placeholder='Select Election Year',
                        value=2025
                    ),
                    width=6
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id='candidate-dropdown-bar',
                            multi=True,
                            placeholder='Select Candidate(s)'
                        )
                    ],
                    width=6
                )
            ],
            style={'marginTop': '20px', 'marginBottom': '10px'}
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
                    html.H4("Monetary Political Contributions to Candidates Over Time", style={'text-align': 'center',
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
                                value=2025
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
        ## Expenditure Time Series Graph
        dbc.Row(
            [
                dbc.Col(
                    html.H4("Political Expenditures Over Time",
                            style={'text-align': 'center', 'marginTop': '20px', 'marginBottom': '20px'}),
                            width=12
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        options=[{'label': candidate, 'value': candidate} for candidate in df['Cand/Committee:'].unique()],
                        id='candidate-dropdown-expenditure',
                        multi=True,
                        placeholder='Select Candidate(s)',
                    ),
                    width=6
                ),
                dbc.Col(
                            dcc.Dropdown(
                                options=[{'label': str(int(year)), 'value': int(year)} for year in df['Election Year'].dropna().unique()],
                                id='year-dropdown-expenditure-ts',
                                placeholder='Select Election Year',
                                value=2025
                            ),
                            width=6
                        )
            ],
            style={'marginTop': '20px', 'marginBottom': '10px'}
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(id='expenditure-timeseries-graph')
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
    [Input('year-dropdown', 'value'), Input('candidate-dropdown-bar', 'value')]
)
def update_graph(selected_year, selected_candidates):
    # Filter for selected year if specified
    filtered_df = df[df['Election Year'] == selected_year] if selected_year else df

    # Filter by selected candidates
    if selected_candidates:
        filtered_df = filtered_df[filtered_df['Cand/Committee:'].isin(selected_candidates)]

    # Seperate contributions and expenditures
    contributions_df = filtered_df[filtered_df['Contact Type:'] == 'Contributor']
    expenditures_df = filtered_df[filtered_df['Contact Type:'] == 'Expenditure']

    # Aggregate total contributions and expenditures for each candidate
    contributions_agg = contributions_df.groupby('Cand/Committee:')['Amount:'].sum().reset_index()
    expenditures_agg = expenditures_df.groupby('Cand/Committee:')['Amount:'].sum().reset_index()

    # Merge dfs on Cand/Committee:
    combined_df = pd.merge(contributions_agg, expenditures_agg, on='Cand/Committee:', how='outer',
                           suffixes=('_contributions', '_expenditures')).fillna(0)
    
    # Graph
    fig = {
        'data': [
            {
                'x': combined_df['Cand/Committee:'].tolist(),
                'y': combined_df['Amount:_contributions'].tolist(),
                'type': 'bar',
                'name': 'Contributions'
            },
            {
                'x': combined_df['Cand/Committee:'].tolist(),
                'y': combined_df['Amount:_expenditures'].tolist(),
                'type': 'bar',
                'name': 'Expenditures'
            }
        ],
        'layout': {
            'title': f'Contributions & Expenditures by Candidate/Committee for {selected_year or "All Years"}',
            'barmode': 'group',
            'xaxis': {'title': 'Candidate/Committee'},
            'yaxis': {'title': 'Total Amount ($)'}
        }
    }
    return fig 

# Callback for timeseries chart
@app.callback(
    Output('timeseries-graph', 'figure'),
    [Input('year-dropdown-ts', 'value'), Input('candidate-dropdown', 'value')]
)
def update_timeseries(selected_year, selected_candidates):
    filtered_df = df[df['strVal'] == 'Monetary Political Contributions']
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
            'title': '',
            'xaxis': {'title': 'Date'},
            'yaxis': {'title': 'Cumulative Contributions ($)'},
            'showlegend': True
        }
    }
    return fig

# Callback for expenditure timeseries graph
@app.callback(
    Output('expenditure-timeseries-graph', 'figure'),
    [Input('year-dropdown-expenditure-ts', 'value'), Input('candidate-dropdown-expenditure', 'value')]
)
def updated_expenditures_timeseries(selected_year, selected_candidates):
    filtered_df = df[df['Contact Type:'] == 'Expenditure']
    if selected_year:
        filtered_df = filtered_df[filtered_df['Election Year'] == selected_year]
    if selected_candidates:
        filtered_df = filtered_df[filtered_df['Cand/Committee:'].isin(selected_candidates)]
    timeseries_df = filtered_df.groupby(['TransDate:', 'Cand/Committee:'])['Amount:'].sum().reset_index()
    timeseries_df = timeseries_df.sort_values(by=['Cand/Committee:', 'TransDate:'])
    timeseries_df['Cumulative Expenditures'] = timeseries_df.groupby('Cand/Committee:')['Amount:'].cumsum()

    fig = {
        'data': [{
            'x': timeseries_df[timeseries_df['Cand/Committee:']==candidate]['TransDate:'],
            'y': timeseries_df[timeseries_df['Cand/Committee:'] == candidate]['Cumulative Expenditures'],
            'type': 'line', 'name': candidate} for candidate in timeseries_df['Cand/Committee:'].unique()],
        'layout': {'title': 'Political Expenditures Over Time',
                   'xaxis': {'title': 'Date'},
                   'yaxis': {'title:': 'Total Expenditures ($)'},
                   'showlegend': True
        }
    }
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)