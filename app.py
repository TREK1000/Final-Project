import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import requests
from io import StringIO

# Load the COVID-19 data
url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
response = requests.get(url)
covid_data = pd.read_csv(StringIO(response.text))

# Melt the dataframe to convert dates from columns to rows
covid_data_melted = covid_data.melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], 
                                    var_name='Date', value_name='Confirmed')

# Convert Date to datetime
covid_data_melted['Date'] = pd.to_datetime(covid_data_melted['Date'])

# Group by Country/Region and Date, summing the Confirmed cases
covid_data_grouped = covid_data_melted.groupby(['Country/Region', 'Date'])['Confirmed'].sum().reset_index()

# Calculate new cases
covid_data_grouped['New_Cases'] = covid_data_grouped.groupby('Country/Region')['Confirmed'].diff().fillna(0)

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1("COVID-19 Dashboard"),
    
    # Date range selector
    dcc.DatePickerRange(
        id='date-range',
        start_date=covid_data_grouped['Date'].min(),
        end_date=covid_data_grouped['Date'].max(),
        display_format='YYYY-MM-DD'
    ),
    
    # Dropdown for country selection
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': country, 'value': country} for country in covid_data_grouped['Country/Region'].unique()],
        value=['US', 'India', 'Brazil'],  # Default selected countries
        multi=True
    ),
    
    # Line chart
    dcc.Graph(id='cases-trend'),
    
    # Bar chart
    dcc.Graph(id='top-countries'),
    
    # Scatter plot
    dcc.Graph(id='cases-vs-new-cases'),
    
    # Summary/Conclusion
    html.Div(id='summary', style={'marginTop': 20, 'padding': 20, 'backgroundColor': '#f0f0f0'})
])

# Callback for updating all graphs and summary
@app.callback(
    [Output('cases-trend', 'figure'),
     Output('top-countries', 'figure'),
     Output('cases-vs-new-cases', 'figure'),
     Output('summary', 'children')],
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('country-dropdown', 'value')]
)
def update_graphs(start_date, end_date, selected_countries):
    # Filter data based on date range and selected countries
    filtered_df = covid_data_grouped[
        (covid_data_grouped['Date'] >= start_date) & 
        (covid_data_grouped['Date'] <= end_date) & 
        (covid_data_grouped['Country/Region'].isin(selected_countries))
    ]
    
    # Line chart: Confirmed cases trend over time
    cases_trend = px.line(filtered_df, x='Date', y='Confirmed', color='Country/Region',
                          title='COVID-19 Confirmed Cases Trend')
    
    # Bar chart: Top countries by total confirmed cases
    top_countries = px.bar(
        filtered_df.groupby('Country/Region')['Confirmed'].last().sort_values(ascending=False).reset_index(),
        x='Country/Region', y='Confirmed', title='Total Confirmed Cases by Country'
    )
    
    # Scatter plot: New cases vs Total cases
    cases_vs_new_cases = px.scatter(filtered_df, x='Confirmed', y='New_Cases', color='Country/Region',
                                    title='New Cases vs Total Cases', log_x=True, log_y=True)
    
    # Generate summary
    total_cases = filtered_df.groupby('Country/Region')['Confirmed'].last().sum()
    total_new_cases = filtered_df.groupby('Country/Region')['New_Cases'].sum().sum()
    top_country = filtered_df.groupby('Country/Region')['Confirmed'].last().idxmax()
    avg_daily_new_cases = total_new_cases / (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days
    
    summary = [
        html.H3("COVID-19 Summary"),
        html.P(f"Total Confirmed Cases: {total_cases:,.0f}"),
        html.P(f"Total New Cases: {total_new_cases:,.0f}"),
        html.P(f"Average Daily New Cases: {avg_daily_new_cases:,.0f}"),
        html.P(f"Country with Most Cases: {top_country}"),
        html.P("Analysis: The dashboard shows the progression of COVID-19 cases across different countries. "
               "The line chart illustrates the trend of confirmed cases over time, while the bar chart compares "
               "total cases between countries. The scatter plot reveals the relationship between total cases and "
               "new cases, which can indicate the current state of the pandemic in each country. This information "
               "can be crucial for understanding the spread of the virus and the effectiveness of containment measures.")
    ]
    
    return cases_trend, top_countries, cases_vs_new_cases, summary

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
