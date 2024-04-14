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

app.layout = html.Div([
    html.H1('Customer Disputes Dashboard'),
    html.Div([
        dcc.Dropdown(
            id='company-dropdown',
            options=[{'label': company, 'value': company} for company in df['company'].unique()],
            value=df['company'].unique()[0]  # Set the default value to the first unique company
        )
    ]),
    dcc.Graph(id='choropleth-map')
])

@app.callback(
    Output('choropleth-map', 'figure'),
    [Input('company-dropdown', 'value')]
)
def update_choropleth_map(company):
    fig = create_choropleth_map(company)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)