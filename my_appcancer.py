#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from sklearn.cluster import KMeans

# Load the dataset
data = pd.read_csv('data_cancer.csv')

# Define the app
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

# Define the app layout
app.layout = html.Div([
    html.H1('Breast Cancer Data Explorer', style={'text-align': 'center', 'color': 'white'}),
    html.Div([
        html.Div([
            html.P('This interactive 3D scatterplot allows you to explore the relationships between various tumor features in the breast cancer dataset. Select the desired features for the X, Y, and Z axes from the dropdown menus below, and the plot will update dynamically.', style={'color': 'white'}),
            html.P('The data points are colored based on the tumor diagnosis (red for malignant, green for benign). You can interact with the plot by rotating, zooming, and panning to identify potential patterns or separations between the two diagnoses.', style={'color': 'white'}),
            html.P('Hover over individual data points to see the corresponding ID and feature values.', style={'color': 'white'}),
            html.Div([
                html.Label('Select X-axis feature:', style={'font-weight': 'bold', 'color': 'white'}),
                dcc.Dropdown(
                    id='x-feature-dropdown',
                    options=[{'label': col, 'value': col} for col in data.columns[2:]],
                    value='radius_mean',
                    style={'width': '100%'}
                )
            ]),
            html.Div([
                html.Label('Select Y-axis feature:', style={'font-weight': 'bold', 'color': 'white'}),
                dcc.Dropdown(
                    id='y-feature-dropdown',
                    options=[{'label': col, 'value': col} for col in data.columns[2:]],
                    value='texture_mean',
                    style={'width': '100%'}
                )
            ]),
            html.Div([
                html.Label('Select Z-axis feature:', style={'font-weight': 'bold', 'color': 'white'}),
                dcc.Dropdown(
                    id='z-feature-dropdown',
                    options=[{'label': col, 'value': col} for col in data.columns[2:]],
                    value='perimeter_mean',
                    style={'width': '100%'}
                )
            ])
        ], style={'width': '30%', 'float': 'left', 'padding': '20px'}),
        html.Div([
            dcc.Graph(id='scatter-plot', style={'height': '800px'})
        ], style={'width': '70%', 'float': 'right', 'padding': '20px'})
    ], style={'display': 'flex', 'justify-content': 'center'}),
    html.Div(style={'clear': 'both'}),
    html.Footer([
        html.Div([
            html.P('The legend in this 3D scatterplot provides information about the different symbols and colors used to represent the tumor diagnosis and cluster assignments.', style={'color': 'white'}),
            html.P('Diagnosis:', style={'color': 'white'}),
            html.Ul([
                html.Li('Red circle (●): Malignant tumor (M)', style={'color': 'white'}),
                html.Li('Green circle (●): Benign tumor (B)', style={'color': 'white'})
            ]),
            html.P('Clusters:', style={'color': 'white'}),
            html.Ul([
                html.Li('Red diamond (◆): Malignant tumors in cluster 0', style={'color': 'white'}),
                html.Li('Red square (■): Malignant tumors in cluster 2', style={'color': 'white'}),
                html.Li('Red plus sign (+): Malignant tumors in cluster 3', style={'color': 'white'}),
                html.Li('Green circle (●): Benign tumors in cluster 1', style={'color': 'white'})
            ])
        ], style={'padding': '20px'})
    ])
])
# Define the callback function
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('x-feature-dropdown', 'value'),
     Input('y-feature-dropdown', 'value'),
     Input('z-feature-dropdown', 'value')])
def update_scatter_plot(x_feature, y_feature, z_feature):
    # Perform clustering with 4 clusters
    X = data[[x_feature, y_feature, z_feature]]
    kmeans = KMeans(n_clusters=4, random_state=0, n_init=10).fit(X)
    data['cluster'] = kmeans.labels_

    # Create the 3D scatterplot
    fig = px.scatter_3d(data, x=x_feature, y=y_feature, z=z_feature,
                        color='diagnosis', color_discrete_map={'M': 'red', 'B': 'green'},
                        hover_name='id', hover_data=[x_feature, y_feature, z_feature, 'cluster'],
                        symbol='cluster', symbol_sequence=["circle", "diamond", "square", "cross"])
    fig.update_layout(
        title=f'3D Scatterplot: {x_feature} vs {y_feature} vs {z_feature}',
        scene=dict(
            xaxis_title=x_feature,
            yaxis_title=y_feature,
            zaxis_title=z_feature,
            camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=-1.8, y=-1.8, z=1.5)
            )
        ),
        width=800,
        height=800,
        margin=dict(l=0, r=0, b=0, t=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True,port=8051)

