import pandas as pd
import plotly.graph_objs as go
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

# Load the data
df = pd.read_csv("consumer_complaints.csv", low_memory=False)

def create_choropleth_map(company):
    # Filter the data for the selected company and disputes
    dispute_presence = df.loc[(df['consumer_disputed?'] == 'Yes') & (df['company'] == company)]

    # Calculate the share of complaints by state
    cross_month = pd.crosstab(dispute_presence['state'], dispute_presence['company']).apply(lambda x: x / x.sum() * 100)
    df_complaints = pd.DataFrame(cross_month[company]).reset_index().sort_values(by=company, ascending=False).round(2)
    df_complaints = df_complaints.rename(columns={company: 'share of complaints'})

    for col in df_complaints.columns:
        df_complaints[col] = df_complaints[col].astype(str)

    scl = [[0.0, 'rgb(202, 202, 202)'], [0.2, 'rgb(253, 205, 200)'], [0.4, 'rgb(252, 169, 161)'],
           [0.6, 'rgb(247, 121, 108)'], [0.8, 'rgb(255, 39, 39)'], [1.0, 'rgb(219, 0, 0)']]

    df_complaints['text'] = "State Code: " + df_complaints['state'] + '<br>'

    data = [dict(
        type='choropleth',
        colorscale=scl,
        autocolorscale=False,
        locations=df_complaints['state'],
        z=df_complaints['share of complaints'],
        locationmode='USA-states',
        text=df_complaints['text'],
        marker=dict(
            line=dict(
                color='rgb(255,255,255)',
                width=2
            )
        ),
        colorbar=dict(
            title="%"
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
    app.run(debug=True, port=8051)