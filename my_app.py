import pandas as pd
import plotly.graph_objs as go
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

# Load the data
df = pd.read_csv("top_100_companies_complaints.csv", low_memory=False)

# Drop duplicate rows
df.drop_duplicates(inplace=True)

# Drop rows with any missing values
df.dropna(how='any', inplace=True)

# Drop columns with any missing values
df.dropna(how='any', axis=1, inplace=True)

import plotly.express as px  # Import plotly.express for color scales

def create_choropleth_map(company):
    # Filter the data for the selected company and disputes
    dispute_presence = df.loc[(df['consumer_disputed?'] == 'Yes') & (df['company'] == company)]

    # Calculate the share of complaints by state
    cross_month = pd.crosstab(dispute_presence['state'], dispute_presence['company']).apply(lambda x: x / x.sum() * 100)
    df_complaints = pd.DataFrame(cross_month[company]).reset_index().sort_values(by=company, ascending=False).round(2)
    df_complaints = df_complaints.rename(columns={company: 'share of complaints'})

    for col in df_complaints.columns:
        df_complaints[col] = df_complaints[col].astype(str)

    # Use a color scale from plotly.express
    colorscale = px.colors.sequential.Plasma  # You can try other color scales like 'Inferno', 'Viridis', 'Magma', etc.

    df_complaints['text'] = "State Code: " + df_complaints['state'] + '<br>' + \
                            "Share of Complaints: " + df_complaints['share of complaints'] + '%'

    data = [dict(
        type='choropleth',
        colorscale=colorscale,
        locations=df_complaints['state'],
        z=df_complaints['share of complaints'].astype(float),  # Convert to float for proper color scaling
        locationmode='USA-states',
        text=df_complaints['text'],
        marker=dict(
            line=dict(
                color='rgb(255,255,255)',
                width=2
            )
        ),
        colorbar=dict(
            title="Share of Complaints (%)"
        )
    )]

    layout = dict(
        title=f'Most Complaints by State <br> {company}',
        geo=dict(
            scope='usa',
            projection=dict(type='albers usa'),
            showlakes=True,
            lakecolor='rgb(255, 255, 255)'
        )
    )

    fig = dict(data=data, layout=layout)
    return fig

app = dash.Dash(__name__)
server= app.server
app.layout = html.Div([
    
    html.Div(style={'max-width': '960px', 'margin': '2rem auto', 'padding': '2rem', 'background-color': 'rgba(255, 255, 255, 0.9)', 'box-shadow': '0 0.5rem 1rem rgba(0, 0, 0, 0.1)', 'border-radius': '0.5rem'}, children=[
        html.Div([
            html.H1('Customer Disputes Dashboard', style={'color': '#222222', 'font-weight': 'bold', 'font-size': '3rem', 'text-shadow': '2px 2px 4px rgba(0, 0, 0, 0.3)', 'animation': 'fadeInDown 1s ease'}),
            html.P('Explore customer complaints across different states and companies: The Customer Disputes Dashboard provides an interactive platform for exploring customer complaints across different states and companies. It offers valuable insights into consumer grievances, enabling users to analyze trends, identify patterns, and gain a deeper understanding of customer sentiment.', style={'font-size': '1.4rem', 'color': '#222222', 'text-shadow': '1px 1px 2px rgba(0, 0, 0, 0.3)', 'margin-top': '0.5rem', 'animation': 'fadeIn 1.5s ease'}),
        ], style={'text-align': 'center', 'margin-bottom': '2rem'}),
        html.Div([
            html.Div([
                html.Label('Select a company:', style={'font-size': '1.2rem', 'color': '#ff4500', 'font-weight': 'bold'}),
                dcc.Dropdown(
                    id='company-dropdown',
                    options=[{'label': company, 'value': company} for company in df['company'].unique()],
                    value=df['company'].unique()[0],
                    style={'width': '100%', 'padding': '0.7rem', 'font-size': '1.1rem', 'border-radius': '0.5rem', 'border': '1px solid #0082c8', 'transition': 'border-color 0.3s', 'background-color': '#f8f9fa'},
                    placeholder="Select a company",
                    clearable=False
                ),
            ], style={'margin-bottom': '1.5rem'}),
            html.Div([
                dcc.Graph(id='choropleth-map', style={'width': '100%', 'border-radius': '0.5rem', 'box-shadow': '0 0.5rem 1rem rgba(0, 0, 0, 0.1)'}),
            ], style={'text-align': 'center'}),
        ], style={'margin-bottom': '2rem'}),
        html.P('Data Source: Consumer Financial Protection Bureau (CFPB) Consumer Complaint Database', style={'font-size': '0.9rem', 'text-align': 'center', 'margin-top': '1rem', 'color': '#6c757d'}),
    ]),
], style={'font-family': 'Helvetica, Arial, sans-serif'})

@app.callback(
    Output('choropleth-map', 'figure'),
    [Input('company-dropdown', 'value')]
)
def update_choropleth_map(company):
    fig = create_choropleth_map(company)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
