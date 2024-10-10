import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import os

# Load the data
df = pd.read_csv('https://raw.githubusercontent.com/TREK1000/Final-Project/refs/heads/main/asset/day_wise.csv')
df['Date'] = pd.to_datetime(df['Date'])

# Initialize the Dash app
app = dash.Dash(__name__)
# Make server variable accessible for Render
server = app.server

# Define the layout
app.layout = html.Div([
    html.H1("COVID-19 Dashboard"),
    
    # Line chart
    html.Div([
        html.H2("Confirmed Cases Over Time"),
        dcc.DatePickerRange(
            id='date-range',
            start_date=df['Date'].min(),
            end_date=df['Date'].max(),
            display_format='YYYY-MM-DD'
        ),
        dcc.Graph(id='line-chart')
    ]),
    
    # Bar chart
    html.Div([
        html.H2("New Cases by Date"),
        dcc.DatePickerSingle(
            id='date-picker',
            min_date_allowed=df['Date'].min(),
            max_date_allowed=df['Date'].max(),
            initial_visible_month=df['Date'].max(),
            date=df['Date'].max()
        ),
        dcc.Graph(id='bar-chart')
    ]),
    
    # Pie chart
    html.Div([
        html.H2("Case Distribution"),
        dcc.Dropdown(
            id='date-dropdown',
            options=[{'label': date, 'value': date} for date in df['Date'].dt.strftime('%Y-%m-%d')],
            value=df['Date'].max().strftime('%Y-%m-%d')
        ),
        dcc.Graph(id='pie-chart')
    ])
])

# Callback for line chart
@app.callback(
    Output('line-chart', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_line_chart(start_date, end_date):
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    fig = px.line(filtered_df, x='Date', y='Confirmed', title='Confirmed Cases Over Time')
    return fig

# Callback for bar chart
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('date-picker', 'date')]
)
def update_bar_chart(selected_date):
    # Get the last 10 days of data up to the selected date
    end_date = pd.to_datetime(selected_date)
    start_date = end_date - pd.Timedelta(days=9)
    
    mask = (df['Date'] > start_date) & (df['Date'] <= end_date)
    filtered_df = df.loc[mask].copy()
    
    fig = px.bar(
        filtered_df,
        x='Date',
        y='New cases',
        title=f'New Cases (Last 10 Days)',
        labels={'New cases': 'New Cases', 'Date': 'Date'}
    )
    return fig

# Callback for pie chart
@app.callback(
    Output('pie-chart', 'figure'),
    [Input('date-dropdown', 'value')]
)
def update_pie_chart(selected_date):
    date_df = df[df['Date'] == selected_date]
    values = [date_df['Active'].values[0], date_df['Recovered'].values[0], date_df['Deaths'].values[0]]
    labels = ['Active', 'Recovered', 'Deaths']
    fig = px.pie(values=values, names=labels, title=f'Case Distribution on {selected_date}')
    return fig

if __name__ == '__main__':
    app.run_server(debug=False)
