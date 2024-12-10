# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into a pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Get the maximum and minimum payload values
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Convert min_payload and max_payload to integers for the RangeSlider
min_payload = int(min_payload)
max_payload = int(max_payload)

# Create a Dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown for Launch Site selection
    html.Br(),
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),
    html.Br(),

    # Pie chart to show success vs failure
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # Payload range slider
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks={i: str(i) for i in range(min_payload, max_payload + 1, 5000)},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # Scatter chart to show payload vs success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback for the success-pie-chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Calculate total success for each site
        success_by_site = spacex_df.groupby('Launch Site')['class'].value_counts().unstack().fillna(0)
        success_counts = success_by_site[1]  # Get the count of successes (class == 1)
        total_success = success_counts.sum()  # Total successes across all sites
        
        # Calculate the percentage of total success for each site
        success_percentage = (success_counts / total_success) * 100
        
        # Create the pie chart showing the percentage of total success for each site
        fig = px.pie(
            names=success_percentage.index,
            values=success_percentage.values,
            title="Percentage of Total Launch Success by Site",
            labels={'Launch Site': 'Success Percentage'}
        )
        
    else:
        # If a specific site is selected, show success/failure for that site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_counts = filtered_df['class'].value_counts()
        
        # Create a pie chart for success vs. failure for the selected site
        fig = px.pie(
            names=success_counts.index,
            values=success_counts.values,
            title=f"Launch Success for {selected_site}",
            labels={'class': 'Success/Failure'}
        )
    
    return fig

# TASK 4: Callback for the success-payload-scatter-chart
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Launch Site',
        title=f"Payload Mass vs. Launch Success for {selected_site}" if selected_site != 'ALL' else "Payload Mass vs. Launch Success"
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
