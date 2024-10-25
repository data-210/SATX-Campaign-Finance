from dash import Dash, dash_table, dcc, html, Input, Output, State
import pandas as pd
from collections import OrderedDict
import dash_bootstrap_components as dbc

df = pd.read_csv('data/campaign_finance20240928.csv')

# Convert TransDate: to date time
df['TransDate:'] = pd.to_datetime(df['TransDate:'], errors='coerce')

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [html.H2("COSA Campaign Finance Data",
                             style={'text-align': 'center'})]
                )
            ]
        ),
        dcc.Download(id='download'),
        dbc.Row(
            [
                dbc.Col(
                    [
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
                        html.Div(id='datatable-interactivity-container')
                    ]
                )
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
                        placeholder='Choose download file type. Default is CSV.',
                    ),
                    width=6
                ),
                dbc.Col(
                    dbc.Button('Download data', id='btn-csv'),
                    width=6
                ),
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
                    dcc.Dropdown(
                        options=[{'label': candidate, 'value': candidate} for candidate in df['Cand/Committee:'].unique()],
                        id='candidate-dropdown',
                        multi=True,
                        placeholder='Select Candidate(s)',
                    ),
                    width=8
                ),
            ],
            style={'marginTop': '20px'}
        ),
        
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(id='timeseries-graph')
                )
            ]
        ),
    ]
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
            'title': f'Contributions for Candidate/Committee for {selected_year or "All Years"}',
            'xaxis': {'title': 'Candidate/Committee'},
            'yaxis': {'title': 'Total Amount ($)'}
        }
    }
    return fig    
# Callback for timeseries chart
@app.callback(
    Output('timeseries-graph', 'figure'),
    [Input('year-dropdown', 'value'), Input('candidate-dropdown', 'value')]
)
def update_timeseries(selected_year, selected_candidates):
    filtered_df = df[df['Contact Type:'] == 'Contributor']
    if selected_year:
        filtered_df = filtered_df[filtered_df['Election Year'] == selected_year]
    
    if selected_candidates:
        filtered_df = filtered_df[filtered_df['Cand/Committee:'].isin(selected_candidates)]
    
    # Aggregate data by TransDate:
    timeseries_df = filtered_df.groupby('TransDate:')['Amount:'].sum().reset_index()

    fig = {
        'data': [{
            'x': timeseries_df['TransDate:'],
            'y': timeseries_df['Amount:'],
            'type': 'line'
        }],
        'layout': {
            'title': 'Candidate Contributions Over Time',
            'xaxis': {'title': 'Date'},
            'yaxis': {'title': 'Total Amount'}
        }
    }
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)