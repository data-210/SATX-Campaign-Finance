from dash import Dash, dash_table, dcc, html, Input, Output, State
from collections import OrderedDict
from pathlib import Path
import logging
import dash_bootstrap_components as dbc
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
DATA = Path.joinpath(REPO, 'data')

df = pd.read_csv(Path.joinpath(DATA, 'campaign_finance20241031.csv'))

# Convert TransDate: to date time
df['TransDate:'] = pd.to_datetime(df['TransDate:'], errors='coerce')
# Add last transaction date and date last downloaded
last_transaction_date = df['TransDate:'].max().strftime('%m/%d/%Y')
data_last_download = '10/31/2024'

app = Dash(__name__)
server = app.server

logging.debug("Starting server...")

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
                        style={'text-align': 'right', 'fontSize': '14px', 'color': '#333333'}
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
                    style={'text-align': 'center', 'font-weight': 'bold', 'color': '#333333'}
                )
            ],
            justify="center",
            align='center',
            style={'marginBottom': '20px'}
        ),      
        dbc.Row(
            [
                dbc.Col(
                    html.H4("Total Contributions & Expenditures",
                            style={'text-align': 'center',
                                   'marginTop': '40px', 
                                   'marginBottom': '15px',
                                   'color': '#1s73e8'}),
                            width=12
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(
                            options=[{'label': candidate, 'value': candidate} for candidate in sorted(df['Cand/Committee:'].unique())],
                            id='candidate-dropdown-bar',
                            multi=True,
                            placeholder='Select Candidate(s)'
                        )
                    ],
                    width=6
                ),
                dbc.Col(
                    dcc.Dropdown(
                        options=[{'label': str(int(year)), 'value': int(year)} for year in sorted(df['Election Year'].dropna().unique())],
                        id='year-dropdown',
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
                    dcc.Graph(id='cand-committee-graph', config={'displayModeBar': False}),
                    width=12,
                    style={
                        'border': '1px solid #e0e0e0',
                        'padding': '20px',
                        'box-shadow': '2px 2px 8px rbga(0,0,0,0.1)',
                        'backgroundColor': 'white'
                    }
                ),
            ],
            style={'marginBottom': '30px'}
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
                        options=[{'label': candidate, 'value': candidate} for candidate in sorted(df['Cand/Committee:'].unique())],
                        id='candidate-dropdown',
                        multi=True,
                        placeholder='Select Candidate(s)',
                    ),
                    width=6
                ),
                dbc.Col(
                            dcc.Dropdown(
                                options=[{'label': str(int(year)), 'value': int(year)} for year in sorted(df['Election Year'].dropna().unique())],
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
                    dcc.Graph(id='timeseries-graph'),
                    width=12,
                    style={
                        'border': '1px solid #e0e0e0',
                        'padding': '20px',
                        'box-shadow': '2px 2px 8px rbga(0,0,0,0.1)',
                        'backgroundColor': 'white'
                    }
                ),
            ],
            style={'marginBottom': '30px'}
        ),
        # Expenditure Time Series Graph
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
                        options=[{'label': candidate, 'value': candidate} for candidate in sorted(df['Cand/Committee:'].unique())],
                        id='candidate-dropdown-expenditure',
                        multi=True,
                        placeholder='Select Candidate(s)',
                    ),
                    width=6
                ),
                dbc.Col(
                            dcc.Dropdown(
                                options=[{'label': str(int(year)), 'value': int(year)} for year in sorted(df['Election Year'].dropna().unique())],
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
                    dcc.Graph(id='expenditure-timeseries-graph'),
                    width=12,
                    style={
                        'border': '1px solid #e0e0e0',
                        'padding': '20px',
                        'box-shadow': '2px 2px 8px rbga(0,0,0,0.1)',
                        'backgroundColor': 'white'
                    }
                ),
            ],
            style={'marginBottom': '30px'}
        ),
#         # Top Donors Table
        dbc.Row(
            [
                dbc.Col(
                    html.H4("Donors & Contributions",
                            style={'text-align': 'center', 'marginTop': '20px', 'marginBottom': '20px'}),
                            width=12
                )
            ]
        ),
        # Row with both tables and drop downs aligned and styled
        dbc.Row(
            [
                # Left: Top Donors Table
                dbc.Col(
                    [
                        html.H5("Top Donors by Total Contributions", style={'text-align': 'center', 'color': '#333333', 'marginBottom':'10px'}),
                        # Election Year dropdown for Top Donors table
                        dcc.Dropdown(
                            options=[{'label': str(int(year)), 'value': int(year)} for year in sorted(df['Election Year'].dropna().unique())],
                            id='donor-year-dropdown',
                            placeholder='Select Election Year',
                            value=2025,
                            style={'marginBottom': '10px'}
                        ),
                        # Candidate Dropdown for Top Donors table
                        dcc.Dropdown(
                            options=[{'label': candidate, 'value': candidate} for candidate in sorted(df['Cand/Committee:'].unique())],
                            id='donor-candidate-dropdown',
                            placeholder='Select Candidate',
                            style={'marginBottom': '20px'}
                        ),
                        # Top Donors Table
                        dash_table.DataTable(
                            id='top-donors-aggregated-table',
                            columns=[
                                {'name': 'Donor Name', 'id': 'Name:'},
                                {'name': 'Total Amount Donated', 'id': 'Total Amount', 'type': 'numeric', 'format': {'specifier': '$,.2f'}},
                                {'name': 'Number of Donations', 'id': 'Donation Count'},
                                {'name': 'Top Candidate', 'id': 'Top Candidate'}
                            ],
                            page_size=10,
                            sort_action='native',
                            style_table={'overflowX': 'auto'},
                            style_header={
                                'backgroundColor': '#f1f1f1',
                                'fontWeight': 'bold',
                                'color': '#333333'
                            },
                            style_cell={'textAlign': 'center'},
                            style_data_conditional=[
                                {'if': {'row_index': 'odd'},
                                 'backgroundColor': '#f9f9f9'}
                            ]
                        )
                    ],
                    width = 6,
                    style={'marginBottom': '20px'}
                ),
                # Right: Average Donation Table
                dbc.Col(
                    [
                        html.H5("Average Donation to Candidates", style={'text-align': 'center', 'color': '#333333', 'marginBottom': '10px'}),
                        # Election Year Dropdown for Average Donation Table
                        dcc.Dropdown(
                            options=[{'label': str(int(year)), 'value': int(year)} for year in sorted(df['Election Year'].dropna().unique())],
                            id='average-donation-year-dropdown',
                            placeholder='Select Election Year',
                            value=2025,
                            style={'marginBottom': '10px'}
                        ),
                        # Candidate Dropdown for Average Donation Table
                        dcc.Dropdown(
                            options=[{'label': candidate, 'value': candidate} for candidate in sorted(df['Cand/Committee:'].unique())],
                            id='average-donation-candidate-dropdown',
                            placeholder='Select Candidate(s)',
                            multi=True,
                            style={'marginBottom': '20px'}
                        ),
                        # Average Donation Table
                        dash_table.DataTable(
                            id='average-donation-table',
                            columns = [
                                {'name': 'Candidate', 'id': 'Cand/Committee:'},
                                {'name': 'Average Donation Amount', 'id': 'Average Donation', 'type': 'numeric', 'format': {'specifier': '$,.2f'}},
                                {'name': 'Number of Donations', 'id': 'Donation Count'},
                                {'name': 'Top Donor', 'id': 'Top Donor'}
                            ],
                            page_size=10,
                            sort_action='native',
                            style_table={'overflowX': 'auto'},
                            style_header={'backgroundColor': '#f1f1f1',
                                          'fontWeight': 'bold',
                                          'color': '#333333'},
                            style_cell={'textAlign': 'center'},
                            style_data_conditional=[
                                {'if': {'row_index': 'odd'},
                                 'backgroundColor': '#f9f9f9'}
                            ]
                        )
                    ],
                    width=6,
                    style={'marginBottom': '20px', 'paddingLeft': '15px'}
                )
            ],
            style={'marginBottom': '20px'}
        )
    ]
)


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
        'layout': {'title': '',
                   'xaxis': {'title': 'Date'},
                   'yaxis': {'title:': 'Total Expenditures ($)'},
                   'showlegend': True
                   }
    }
    return fig


# # Callback for Top Donors Table
@app.callback(
    Output('top-donors-aggregated-table', 'data'),
    [Input('donor-year-dropdown', 'value'), Input('donor-candidate-dropdown', 'value')]
)
def update_top_donors_aggregated_table(selected_year, selected_candidate):
    # Filter for contributors in selected year
    contributors_df = df[(df['Contact Type:'] == 'Contributor') & (df['Election Year'] == selected_year)]
    if selected_candidate:
        contributors_df = contributors_df[contributors_df['Cand/Committee:'] == selected_candidate]

    # Check for data
    if contributors_df.empty:
        return []

    # Aggregate data by donor
    top_donors = contributors_df.groupby('Name:').agg(
        **{
            'Total Amount': ('Amount:', 'sum'),
            'Donation Count': ('Amount:', 'size')
        }
    ).reset_index()

    # Identify top candidate by amount for each donor
    top_candidate_df = contributors_df.groupby(['Name:', 'Cand/Committee:'])['Amount:'].sum().reset_index()
    top_candidate_df = top_candidate_df.loc[top_candidate_df.groupby('Name:')['Amount:'].idxmax()]
    top_donors = top_donors.merge(top_candidate_df[['Name:', 'Cand/Committee:']], on='Name:')
    top_donors.rename(columns={'Cand/Committee:': 'Top Candidate'}, inplace=True)

    # Sort by total amount and select top 10 donors
    top_donors = top_donors.sort_values(by='Total Amount', ascending=False)#.head(10)

    return top_donors.to_dict('records')


# Callback for Average Donation Table
@app.callback(
    Output('average-donation-table', 'data'),
    [Input('average-donation-year-dropdown', 'value'), Input('average-donation-candidate-dropdown', 'value')]
)
def update_average_donation_table(selected_year, selected_candidate):
    filtered_df = df[(df['Contact Type:'] == 'Contributor') & (df['Election Year'] == selected_year)]

    if selected_candidate:
        filtered_df = filtered_df[filtered_df['Cand/Committee:'].isin(selected_candidate)]

    if filtered_df.empty:
        return []

    avg_donation_df = filtered_df.groupby('Cand/Committee:').agg(
        Average_Donation = ('Amount:', 'mean'),
        Donation_Count = ('Amount:', 'size')
    ).reset_index()

    top_donor_df = filtered_df.groupby(['Cand/Committee:', 'Name:'])['Amount:'].sum().reset_index()
    top_donor_df = top_donor_df.loc[top_donor_df.groupby('Cand/Committee:')['Amount:'].idxmax()]
    avg_donation_df = avg_donation_df.merge(top_donor_df[['Cand/Committee:', 'Name:']], on='Cand/Committee:')
    avg_donation_df.rename(columns={'Average_Donation': 'Average Donation', 'Donation_Count': 'Donation Count', 'Name:': 'Top Donor'}, inplace=True)

    # Sort by Average Donation
    avg_donation_df = avg_donation_df.sort_values(by='Average Donation', ascending=False)

    return avg_donation_df.to_dict('records')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
    app.run_server(debug=True)