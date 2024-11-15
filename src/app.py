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
        # Update with global dropdown
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        options=[{'label': str(int(year)), 'value': int(year)} for year in sorted(df['Election Year'].dropna().unique())],
                        id='global-year-dropdown',
                        placeholder='Select Election Year',
                        value=2025,
                        style={'marginBottom': '10px'}
                    ),
                    width=6
                ),
                dbc.Col(
                    dcc.Dropdown(
                        options=[{'label': candidate, 'value': candidate} for candidate in sorted(df['Cand/Committee:'].unique())],
                        id='global-candidate-dropdown',
                        multi=True,
                        placeholder='Select Candidate(s)',
                        style={'marginBottom': '10px'}
                    ),
                    width=6
                ),
            ],
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
                ),
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
                ),
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
                ),
                #Top Donors Table
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
                
            ],
            style={'marginBottom': '20px'}
        ),
        # Download the Data
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4("Download the Data", style={'text-align': 'center', 'color': '#333333', 'marginTop': '30px'}),
                        html.P(
                            """
                            The complete campaign finance dataset used in this application is available from the City of San Antonio's campaign finance website and Data210's GitHub repository.
                            """,
                            style={'text-align': 'justify', 'color': '#333333', 'marginTop': '15px'}
                        ),
                        html.Ul(
                            [
                                html.Li(html.A("City of San Antonio Campaign Finance Page", href="https://webapp1.sanantonio.gov/campfinsearch/search.aspx",
                                               target="_blank", style={'color': '#1a73e8'})),
                                html.Li(html.A("Data210 GitHub Repository for Full Dataset", href="https://github.com/data-210/SATX-Campaign-Finance/tree/63e582011c14becc00d8e3ad4bfe0edbf714999d/data",
                                               target="_blank", style={'color': '#1a73e8'}))
                                               
                            ],
                            style={'marginTop': '10px'}
                        )
                    ],
                    width=12,
                    style={'padding': '20px', 'backgroundColor': '#f9f9f9', 'borderTop': '1px solid #e0e0e0'}
                )
            ],
            style={'marginTop': '30px'}
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4("Methodology", style={'text-align': 'center', 'color': '#333333', 'marginTop': '20px'}),
                        html.P(
                            """
                            This City of San Antonio Campaign Finance dashboard was created to provide insights into political donations and expenditures of candidates for San Antonio's various political offices.
                            Users can explore previous election years' campaign finance figures as well as upcoming elections.
                            The graphs and tables above provide detail about each candidate's expenditures and donations, as well as top donors to each candidate and the average donation amount each candidate receives.
                            This effort was influenced by a curiosity about how candidates for San Antonio City Council and Mayor raise money, spend money, how much money is involved in these campaigns, and who is donating money to candidates.
                            As Article VII of the City Charter, which covers campaign finance, says:  "It is essential in a democratic system that the public has confidence in the integrity, independence, and impartiality of those who are elected to act on their behalf in government. There is a public perception that a relationship exists between substantial contributions and access to elected officials. To diminish the perceived or actual connection between contributions and influence, the city adopts this Campaign Finance Code to promote public confidence and, it is hoped, a greater degree of citizen participation in the electoral process."
                            We hope that this dashboard encourages San Antonio voters to learn more about how candidates who wish to represent them in city government are funded.
                            """,
                            style={'text-align': 'justify', 'color': '#333333', 'marginTop': '15px'}
                        ),
                        html.P(
                            """
                            The first graph of the dashboard, Total Contributions and Expenditures, shows the sum total of all donations to each candidate and the sum total of all expenditures made by the same candidate.
                            Users can use the Election Year dropdown to view data for the previous election years or for the next City election year (2025). 
                            The Election Year dropdown values come from the campaign finance reports submitted by the candidates. When candidates submit a campaign finance report detailing a donation or an expenditure, the election year for that particular report must be specified.
                            The candidate dropdown values come from the Cand/Committee: column of the campaign finance data. Users have the ability to select multiple candidates and examine the contributions and expenditures for each.
                            For example, if you wanted to see donations and expenditures for Councilwoman Kaur and former Councilman Bravo (District 1) in the 2023 City Council election, you would select '2023' from the Election Year dropdown and select Sukh Kaur and Mario Bravo in the candidate dropdown.
                            """,
                            style={'text-align': 'justify', 'color': '#333333', 'marginTop': '15px'}
                        ),
                        html.P(
                            """
                            The next two graphs show contributions and expenditures over time for each candidate in a given election year. 
                            These graphs show how much money candidates have received over the course of a calendar year for a given election. It also shows how much money candidates have spent over time for a given election year.
                            The Election Year and Candidate dropdown menus work the same way as the Total Contributions and Expenditures dropdowns.
                            Users can choose an election year and either one or several candidates to view how much money their campaigns received over time and how much money the candidates spent as the year progresses.
                            Sticking with the Councilwoman Kaur and former Councilman Bravo example, the user can see the Bravo started receiving contributions for Election Year 2023 much sooner than Councilwoman Kaur did and that he raised more money overall.
                            Bravo also spent more money during the campaign that Kaur, but ended up losing the election.
                            """,
                            style={'text-align': 'justify', 'color': '#333333', 'marginTop': '15px'}
                        ),
                        html.P(
                            """
                            The final two tables of the dashboard show Top Donors by Total Contributions and Average Donations to Candidates.
                            The first table, Top Donors by Total Contributions, allows users to see who the top donor is to each candidate. 
                            Election Year 2025 is the default option for this table, but users can choose any election year and candidate they want.
                            The table is automatically sorted by the "Total Amount Donated" column (largest donation to smallest), but the user has the option to sort by the other columns, as well.
                            Users can also see how many times a donor has contributed to a candidate. For example, for Election Year 2025, Councilwoman Kaur's top donor has made 5 contributions totaling $2,500.
                            """,
                            style={'text-align': 'justify', 'color': '#333333', 'marginTop': '15px'}
                        ),
                        html.P(
                            """
                            The second table shows Average Donations to Candidates. The final column of the table also shows who that candidate's top donor is.
                            Like the table above, users can choose different election years but can also select multiple candidates for comparison.
                            Let's look at the race between Sukh Kaur and Mario Bravo again. By selecting Election Year 2023 and those candidates, the user can see that Bravo's average donation was $320.00 and Kaur's was $282.02.
                            Bravo also received a lower number of donations compared to Kaur. 
                            """,
                            style={'text-align': 'justify', 'color': '#333333', 'marginTop': '15px'}
                        ),
                        html.P(
                            """
                            This dashboard will continue to be updated on a monthly basis. If there any questions, feature requests, comments, or problems with the data, we'd love to hear from you!
                            You can reach out at jack@data210.com.
                            """
                        )
                    ]
                )
            ]
        )
    ]
)


# Callback for updating candidate-based bar graph
@app.callback(
    Output('cand-committee-graph', 'figure'),
    [Input('global-year-dropdown', 'value'), Input('global-candidate-dropdown', 'value')]
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
    [Input('global-year-dropdown', 'value'), Input('global-candidate-dropdown', 'value')]
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
    [Input('global-year-dropdown', 'value'), Input('global-candidate-dropdown', 'value')]
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