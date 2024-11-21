    
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html

# Load the data
url = "https://raw.githubusercontent.com/plotly/datasets/master/MTA_Ridership_by_DATA_NY_GOV.csv"
data = pd.read_csv(url)

# Convert 'Date' column to datetime format and extract month, year, and day of the week
data['Date'] = pd.to_datetime(data['Date'])
data['Year'] = data['Date'].dt.year
data['Month'] = data['Date'].dt.month
data['Day'] = data['Date'].dt.day_name()

# Rename columns for simplicity
data.rename(columns={
    'Subways: Total Estimated Ridership': 'Subways',
    'Buses: Total Estimated Ridership': 'Buses',
    'LIRR: Total Estimated Ridership': 'LIRR',
    'Metro-North: Total Estimated Ridership': 'Metro-North',
    'Access-A-Ride: Total Scheduled Trips': 'Access-A-Ride',
    'Bridges and Tunnels: Total Traffic': 'Bridges and Tunnels',
    'Staten Island Railway: Total Estimated Ridership': 'Staten Island Railway',
    'Subways: % of Comparable Pre-Pandemic Day': 'Subways %',
    'Buses: % of Comparable Pre-Pandemic Day': 'Buses %',
    'LIRR: % of Comparable Pre-Pandemic Day': 'LIRR %',
    'Metro-North: % of Comparable Pre-Pandemic Day': 'Metro-North %',
    'Access-A-Ride: % of Comparable Pre-Pandemic Day': 'Access-A-Ride %',
    'Bridges and Tunnels: % of Comparable Pre-Pandemic Day': 'Bridges and Tunnels %',
    'Staten Island Railway: % of Comparable Pre-Pandemic Day': 'Staten Island Railway %'
}, inplace=True)

# Calculate total ridership by summing all relevant columns
data['Total Ridership'] = (
    data['Subways'] +
    data['Buses'] +
    data['LIRR'] +
    data['Metro-North'] +
    data['Access-A-Ride'] +
    data['Bridges and Tunnels'] +
    data['Staten Island Railway']
)

# Calculate the percentage of ridership by segment for both 2020 and 2024
segments = ['Subways', 'Buses', 'LIRR', 'Metro-North', 'Access-A-Ride', 'Bridges and Tunnels', 'Staten Island Railway']

# Filter data for 2020 and 2024
data_2020 = data[data['Year'] == 2020]
data_2024 = data[data['Year'] == 2024]

# Calculate percentage for 2020
data_2020_percent = {segment: (data_2020[segment].sum() / data_2020['Total Ridership'].sum()) * 100 for segment in segments}

# Calculate percentage for 2024
data_2024_percent = {segment: (data_2024[segment].sum() / data_2024['Total Ridership'].sum()) * 100 for segment in segments}

# Prepare data for the bar chart
chart_data_2020 = pd.DataFrame(list(data_2020_percent.items()), columns=['Transport Mode', '2020 Percentage'])
chart_data_2024 = pd.DataFrame(list(data_2024_percent.items()), columns=['Transport Mode', '2024 Percentage'])

# Merge the two datasets for easy comparison
chart_data = pd.merge(chart_data_2020, chart_data_2024, on='Transport Mode')

# Reshape the data so that we have one row per transport mode and year
chart_data_melted = chart_data.melt(id_vars=["Transport Mode"], value_vars=["2020 Percentage", "2024 Percentage"], 
                                    var_name="Year", value_name="Percentage")

# Sort the data by percentage in descending order
chart_data_melted = chart_data_melted.sort_values('Percentage', ascending=False)

# Create the bar chart with separate bars for 2020 and 2024
fig = px.bar(
    chart_data_melted,
    y='Transport Mode',
    x='Percentage',
    color='Year',
    barmode='group',  # Group bars for 2020 and 2024
    title='Percentage of Ridership by Transport Mode in 2020 and 2024',
    labels={'Transport Mode': 'Transport Mode', 'Percentage': 'Percentage (%)'},
    color_discrete_sequence=px.colors.qualitative.Set2,
    text='Percentage'  # Add percentage values as text on bars
)

# Customize the text and layout
fig.update_traces(
    texttemplate='%{text:.2f}%',  # Format text to show 2 decimal places
    textposition='inside'  # Position text inside the bars
)

# Remove axis titles and put labels below
fig.update_layout(
    xaxis_title=None,  # Remove title for the x-axis
    yaxis_title=None,  # Remove title for the y-axis
    xaxis=dict(tickangle=0),  # Set the angle for x-axis labels to horizontal
    yaxis=dict(tickangle=0),  # Set the angle for y-axis labels to horizontal
    showlegend=True,
    width=800,  # Adjust the width of the chart (e.g., 800 pixels)
    xaxis_tickangle=-45,  # Rotate x-axis labels to make them more readable
    margin={'l': 50, 'r': 50, 't': 50, 'b': 150},  # Add bottom margin to space out the x labels
)

# Move the legend below the chart
fig.update_layout(
    legend=dict(
        orientation="h",  # Horizontal layout
        yanchor="bottom",  # Anchor to the bottom
        y=-0.3,  # Position below the chart
        xanchor="center",  # Center the legend horizontally
        x=0.5  # Position in the middle
    ),
    showlegend=True,
    width=500,  # Adjust the width of the chart (e.g., 1000 pixels)
)
# Reduce font size of title
fig.update_layout(
    title_font=dict(
        family="Arial, sans-serif", 
        size=16,  # Reduced font size
        color="black", 
        weight="bold"
    ),
    height=500  # Increase the height of the chart
)
# Initialize Dash app with suppress_callback_exceptions=True
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Define transportation modes and years for the dropdown
transport_modes = ['Subways', 'Buses', 'LIRR', 'Metro-North', 'Access-A-Ride', 'Bridges and Tunnels', 'Staten Island Railway']
years = sorted(data['Year'].unique())

# Define sidebar layout with page links
sidebar = html.Div(
    [
        html.H2("Metropolitan Transport Authority (MTA)", style={'textAlign': 'left', 'color': '#FFFFFF'}),
        html.Hr(),
        dcc.Link('About', href='/about', style={'display': 'block', 'padding': '10px', 'fontSize': '18px', 'color': '#FFFFFF'}),
        dcc.Link('Overview', href='/overview', style={'display': 'block', 'padding': '10px', 'fontSize': '18px', 'color': '#FFFFFF'}),
        dcc.Link('Segment', href='/segment', style={'display': 'block', 'padding': '10px', 'fontSize': '18px', 'color': '#FFFFFF'}),
    ],
    style={
        'width': '20%', 'display': 'inline-block', 'verticalAlign': 'top',
        'padding': '20px', 'backgroundColor': '#1f2e45', 'height': '100vh'
    }
)
# Define the layout for the About, Overview, and Segment pages
about_page = html.Div([
    html.H1("About Page")
])

overview_page = html.Div([
    html.H1("Overview Page")
])

segment_page = html.Div([
    html.H1("Segment Page")
])

# Define the layout for the app
app.layout = html.Div(
    [
        dcc.Location(id='url', refresh=False),  # To track the URL
        sidebar,  # Sidebar layout
        html.Div(id='page-content')  # Content based on the current page
    ],
    style={'display': 'flex'}
)

# About Page
about_page = html.Div(
    [
        # Container for Image and Heading
        html.Div(
            [
                # Left side: Heading
                html.H1(
                    "The Metropolitan Transportation Authority",
                    style={
                        'position': 'absolute',
                        'top': '50%',
                        'left': '35px',
                        'transform': 'translateY(-50%)',
                        'color': 'white',
                        'font-size': '36px',
                        'text-shadow': '2px 2px 4px rgba(0, 0, 0, 0.5)',
                        'z-index': '10',
                    }
                ),
                # Image at the top
                html.Img(
                    src="https://a.loveholidays.ie/media-library/~production/74f669f2278072d261f503d89e6b884b431a082d-3200x1173.jpg?auto=avif%2Cwebp&quality=80&dpr=1.5&optimize=high&fit=crop&width=1280&height=380",
                    style={'width': '100%', 'max-width': '5000px', 'height': 'auto', 'display': 'block', 'margin': '0 auto'}
                ),
            ],
            style={
                'position': 'relative',
                'width': '100%',
                'height': '380px',
                'margin-bottom': '0'
            }
        ),
        # Flex container for text and chart side by side
        html.Div(
            [
                # Left side: Text content
                html.Div(
                    [
                        html.P(
                            "The Metropolitan Transportation Authority (MTA) is the largest public transportation network "
                            "in the United States, serving the New York metropolitan area. It operates a vast network of subway, "
                            "bus, and commuter rail services across the five boroughs of New York City, as well as parts of the surrounding "
                            "counties. The MTA plays a critical role in keeping the region's transportation system running efficiently, "
                            "delivering over 8 million daily rides to commuters and travelers."
                        ),
                
                        html.P(
                            "The MTA is responsible for managing a wide range of services: "
                            "the New York City Subway, local and express buses, the Long Island Rail Road (LIRR), Metro-North Railroad, "
                            "Staten Island Railway, Access-A-Ride, and several bridges and tunnels. "
                            "It also maintains a significant part of the region's infrastructure, including the extensive network of bridges, tunnels, "
                            "and the construction of new projects such as the Second Avenue Subway and the East Side Access project."
                        ),
                        html.P(
                            "Over 56% of ridership comes from the Subway, followed by Buses and Bridges and Tunnels." 
                            "In 2020, Bridges and Tunnels had the second-highest ridership, but by 2024, it dropped to third place."
                        ),
                    ],
                    style={'flex': 1, 'textAlign': 'justify', 'padding': '20px', 'width': '70%','Top-margin': '0'}
                ),
                # Right side: Bar chart
                html.Div(
                    [
                        dcc.Graph(
                            id='ridership-bar-chart',
                            figure=fig
                        )
                    ],
                    style={'flex': 1, 'padding': '20px'}
                ),
            ],
            style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'flex-start',
                'margin-right': '10px'  # Reduce right margin of the page
            }
        ),
    ],
    style={
        'margin-right': '10px',  # Reduce overall page right margin
        'margin-left': '10px'   # Optional: Adjust left margin for balance
    }
)


# Add the layout to the app
app.layout = sidebar

if __name__ == '__main__':
    app.run_server(debug=True)


# Overview Page with KPIs and Line chart
overview_page = html.Div(
    [
        # Image Container with Heading
        html.Div([
            html.Img(
                src="https://www.immihelp.com/assets/cms/traveling-via-metros-and-subways-in-the-us-newcomers-guide.jpg",  # Replace with your image URL
                style={
                    'width': '100%',  # Make it span the entire width
                    'height': '250px',  # Set the height of the image (cropped)
                    'object-fit': 'cover',  # Crop the image to fill the space
                    'object-position': 'center',  # left the image
                    'borderRadius': '10px',  # Optional: Add rounded corners
                    'position': 'relative'  # Allow absolute positioning of text over the image
                }
            ),
            
            # Heading on top of the image
            html.H1(
                "Overview of MTA Ridership",
                style={
                    'position': 'absolute',
                    'top': '50%',  # Position the heading vertically in the middle of the image
                    'left': '20%', # Center horizontally
                    'bottom':'300px',  # Place text at the bottom of the image
                    'left': '250px',  # Place text to the left of the image
                    'transform': 'translate(-50%, -50%)',  # Offset to truly center the text
                    'color': 'white',  # White text
                    'fontSize': '36px',  # Adjust font size
                    'fontWeight': 'bold',
                    'textShadow': '2px 2px 4px rgba(0,0,0,0.5)',  # Optional shadow for better readability
                }
            ),
        ], style={'position': 'relative', 'marginBottom': '20px'}),  # Space below the image and heading

        # Flex container for the text and dropdown slicer section
        html.Div([
            # Text Section Next to the Dropdown Slicer
            html.Div([
                html.P(
                    "In this section, you can observe the trends and patterns in MTA ridership, "
                    "including an overview of the total ridership, the impact of the pandemic, and how current ridership compares "
                    "to pre-pandemic levels. The line chart below displays the historical ridership data over time, while the KPIs provide "
                    "a snapshot of the most recent metrics, including total ridership and its comparison to previous years."
                    " The overall ridership has not yet returned to its pre-pandemic levels, showing a 15% decrease in 2024 compared to 2023.",
                    style={
                        'textAlign': 'justify',  # Justify the text
                        'padding': '10px',
                        'fontSize': '16px',  # Set font size to 14px
                        'color': '#333',
                        'backgroundColor': '#FFFFFF',  # Light background color for the text section
                        'borderRadius': '8px',
                        'marginBottom': '10px',  # Reduced the space below the text
                        'flex': '1',  # Allow the text section to take available space
                        'marginRight': '50px',  # Add space between text and dropdown
                        'width': '100%',
                    }
                ),
            ], style={
                'flex': '1',  # Take up available space for the text section
                'textAlign': 'left'
            }),
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'marginBottom': '10px',  # Reduce the space between text section and dropdown slicer
        }),

        # Dropdown for Year Selection (Positioned below the image)
        html.Div([
            dcc.Dropdown(
                id='overview-year-dropdown',
                options=[{'label': str(year), 'value': year} for year in sorted(data['Year'].unique())],
                value=data['Year'].max(),  # Default to the most recent year
                style={'width': '40%', 'padding': '5px', 'display': 'inline-block',}
            )
        ], style={
            'textAlign': 'right', 'padding': '10px', 'marginLeft': '10px', 'borderRadius': '5px', 'marginTop': '10px', 'flexDirection': 'column',
            'alignItems': 'flex-end', 'width': '100%', 'marginBottom': '5px'
        }),

        # Flex container for KPI cards (side by side) and line chart
        html.Div([
            # Left side: KPI Card 1 (Total Ridership)
            html.Div([
                html.H3("Overview Total Ridership (in millions)", style={'color': 'solid grey', 'fontSize': 16}),
                html.P(id="Overview-kpi-card", style={'fontSize': 18, 'color': 'black', 'fontWeight': 'bold'}),
                html.P(id="Overview-kpi-yoy-diff", style={'fontSize': 12, 'color': 'black'}),
            ], style={
                'padding': '10px',
                'backgroundColor': '#E6E6FA',
                'border': '1px solid grey',
                'borderRadius': '10px',
                'height': '140px',
                'boxSizing': 'border-box',
                'color': 'black',
                'marginBottom': '15px',
                'width': '40%',  # Reduced width for side-by-side display
                'marginRight': '2%',  # Small gap between the two KPI cards
                'marginTop': '10px',  # Reduced margin-top for KPI cards
            }),

            # Right side: KPI Card 2 (Pre-pandemic Ridership)
            html.Div([
                html.H3("Overview Average % of Pre-Pandemic Ridership", style={'color': 'solid grey', 'fontSize': 16}),
                html.P(id="Overview-kpi-pre-pandemic", style={'fontSize': 18, 'color': 'black', 'fontWeight': 'bold'}),
                html.P(id="Overview-kpi-pre-pandemic-yoy", style={'fontSize': 12, 'color': 'black'}),
            ], style={
                'padding': '10px',
                'backgroundColor': '#E6E6FA',
                'border': '1px solid grey',
                'borderRadius': '10px',
                'height': '140px',
                'boxSizing': 'border-box',
                'color': 'black',
                'marginBottom': '15px',
                'width': '40%',  # Reduced width for side-by-side display
                'marginLeft': '2%',  # Small gap between the two KPI cards
                'marginTop': '10px',  # Reduced margin-top for KPI cards
            }),
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'}),  # Flex container to display both cards side by side

        # Line Chart placed below the KPI Cards
        html.Div([
            dcc.Graph(id='overview-ridership-graph'),
        ], style={
            'width': '100%',
            'padding': '5px',
            'backgroundColor': '#FFFFFF',
            'borderRadius': '10px',
            'color': 'black',
            'marginTop': '20px',  # Space above the chart to separate it from the KPI cards
        }),

    ]
)

# Segment Page (example)
segment_page = html.Div([
    # Image Container with Heading
    html.Div([
        html.Img(
            src="https://www.immihelp.com/assets/cms/traveling-via-metros-and-subways-in-the-us-newcomers-guide.jpg",  # Replace with your image URL
            style={
                'width': '100%',  # Make it span the entire width
                'height': '250px',  # Set the height of the image (cropped)
                'object-fit': 'cover',  # Crop the image to fill the space
                'object-position': 'center',  # Center the image
                'borderRadius': '10px',  # Optional: Add rounded corners
                'position': 'relative'  # Allow absolute positioning of text over the image
            }
        ),
        
        # Heading on top of the image
        html.H1(
            "Ridership Segment Analysis",
            style={
                'position': 'absolute',
                'top': '50%',  # Position the heading vertically in the middle of the image
                'left': '20%', # Center horizontally
                'bottom': '300px',  # Place text at the bottom of the image
                'left': '250px',  # Place text to the left of the image
                'transform': 'translate(-50%, -50%)',  # Offset to truly center the text
                'color': 'white',  # White text
                'fontSize': '36px',  # Adjust font size
                'fontWeight': 'bold',
                'textShadow': '2px 2px 4px rgba(0,0,0,0.5)',  # Optional shadow for better readability
            }
        ),
    ], style={'position': 'relative', 'marginBottom': '20px'}),  # Space below the image and heading
    
    # Flex container for the text and dropdown slicer section
        html.Div([
            # Text Section Next to the Dropdown Slicer
            html.Div([
                html.P(
                    "In this section, you can observe the trends and patterns in MTA ridership, "
                    "including an overview of the total ridership, the impact of the pandemic, and how current ridership compares "
                    "to pre-pandemic levels. The line chart below displays the historical ridership data over time, while the KPIs provide "
                    "a snapshot of the most recent metrics, including total ridership and its comparison to previous years."
                    "In 2023, subway ridership posted a 14% annual increase to 1.15 billion annual paid rides, hitting the billion-ride milestone six weeks earlier than in 2022."
                    "Ridership patterns have shifted since the beginning of the COVID-19 pandemic, with discretionary travel becoming more popular than commutation travel. Increased telecommuting and more flexible work-from-home policies have made traditional five-day commuting less common.",
                    style={
                        'textAlign': 'justify',  # Justify the text
                        'padding': '10px',
                        'fontSize': '16px',  # Set font size to 14px
                        'color': '#333',
                        'backgroundColor': '#FFFFFF',  # Light background color for the text section
                        'borderRadius': '8px',
                        'marginBottom': '0px',
                        'flex': '1',  # Allow the text section to take available space
                        'marginRight': '50px',  # Add space between text and dropdown
                        'Width':'30%',
                    }
                ),
            ], style={
                'flex': '1',  # Take up available space for the text section
                'textAlign': 'left'
            }),
            ]),
    # Dropdowns for selecting Mode and Year
    html.Div([
        # Mode Dropdown
        html.Div([
            html.Label("Select Transportation Mode:"),
            dcc.Dropdown(
                id='mode-dropdown',
                options=[{'label': mode, 'value': mode} for mode in transport_modes],
                value='Subways',  # Default value
                clearable=False
            )
        ], style={'width': '20%', 'position': 'relative','padding': '5px', 'display': 'inline-block'}),

        # Year Dropdown
        html.Div([
            html.Label("Select Year:"),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(year), 'value': year} for year in years],
                value=years[-1],  # Default to the most recent year
                clearable=False
            )
        ], style={'width': '20%', 'padding': '5px', 'display': 'inline-block'}),
    ], style={'textAlign': 'right', 'padding': '3px', 'marginLeft': '10px'}),

    # Flex container for KPI cards and line chart
    html.Div([
        # Left side: KPI Cards
        html.Div([
            # KPI Card 1: Total Ridership
            html.Div([
                html.H3("Total Ridership (in millions)", style={'color': 'solid grey', 'fontSize': 14}),
                html.P(id="kpi-card", style={'fontSize': 16, 'color': 'black', 'fontWeight': 'bold'}),
                html.P(id="kpi-yoy-diff", style={'fontSize': 12, 'color': 'black'}),
            ], style={
                'padding': '10px',
                'backgroundColor': '#E6E6FA',
                'border': '1px solid grey',
                'borderRadius': '5px',
                'height': '140px',
                'boxSizing': 'border-box',
                'color': 'black',
                'marginBottom': '15px',
                'width': '80%',
                'marginTop': '30px',
            }),

            # KPI Card 2: Average % of Pre-Pandemic Ridership
            html.Div([
                html.H3("Average % of Pre-Pandemic Ridership", style={'color': 'solid grey', 'fontSize': 14}),
                html.P(id="kpi-pre-pandemic", style={'fontSize': 16, 'color': 'black', 'fontWeight': 'bold'}),
                html.P(id="kpi-pre-pandemic-yoy", style={'fontSize': 12, 'color': 'black'})
            ], style={
                'padding': '10px',
                'backgroundColor': '#E6E6FA',
                'border': '1px solid grey',
                'borderRadius': '5px',
                'height': '140px',
                'boxSizing': 'border-box',
                'color': 'black',
                'marginBottom': '15px',
                'width': '80%'
            }),
        ], style={
            'width': '100%',
            'display': 'inline-block',
            'padding': '10px',
            'verticalAlign': 'top',
            'backgroundColor': '#FFFFFF',
            'borderRadius': '10px',
            'color': 'black',
            'marginRight': '10px',
        }),

        # Right side: Line Chart
        html.Div([
            dcc.Graph(id='trend-graph')
        ], style={
            'width': '250%',
            'display': 'inline-block',
            'padding': '5px',
            'backgroundColor': '#FFFFFF',
            'borderRadius': '10px',
            'height': '390px',
            'boxSizing': 'border-box',
            'color': 'black',
            'marginLeft': '2',
        }),

    ], style={'display': 'flex', 'alignItems': 'flex-start', 'justifyContent': 'space-between'}),  # Flex container


    # Summary Table (Below KPIs and Chart)
    html.Div([
        dash_table.DataTable(
            id='summary-table',
            columns=[
                {"name": "Year", "id": "Year"},
                {"name": "Weekday", "id": "Weekday"},
                {"name": "Weekend", "id": "Weekend"},
                {"name": "Sunday", "id": "Sunday"},
                {"name": "Total", "id": "Total"}
            ],
            style_table={'margin-top': '10px', 'margin-right': '10px', 'margin-bottom': '10px', 'margin-left': '10px'},
            style_cell={'textAlign': 'center', 'padding': '5px', 'fontSize': 12}
        ),
    ], style={'width': '100%'}),  # Table below the KPIs and chart

])


# Main Layout: Sidebar + Page Content
app.layout = html.Div(
    [
        dcc.Location(id='url', refresh=False),
        html.Div(
            children=[
                sidebar,  # Assuming the sidebar code is elsewhere
                html.Div(id='page-content', style={'width': '70%', 'display': 'inline-block', 'padding': '20px'})
            ],
            style={'display': 'flex', 'alignItems': 'start'}
        ),
    
        # Footer Note
        html.Div(
            children=[
                html.P(
                    children=[
                        "Maven Commuter Challenge | Analysis by Mona | ",
                        html.A("LinkedIn", href="https://www.linkedin.com/in/mona-swarnakar-2698111a/", target="_blank")
                    ],
                    style={'textAlign': 'left', 'color': 'gray', 'fontSize': 12, 'margin': '15px'}
                )
            ],
            style={'backgroundColor': '#FFFFFF', 'position': 'relative', 'width': '100%'}
        )
    ]  # <-- Closing the outer list here
)  # <-- Closing the final parenthesis here for app.layout


# Callback to update the page content based on URL
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/about':
        return about_page
    elif pathname == '/overview':
        return overview_page
    elif pathname == '/segment':
        return segment_page
    else:
        return about_page  # Default page

# Callback to update the sidebar text color based on the active page
@app.callback(
    [Output('about-link', 'style'),
     Output('overview-link', 'style'),
     Output('segment-link', 'style')],
    [Input('url', 'pathname')]
)
def highlight_active_link(pathname):
    # Default link style
    inactive_style = {'display': 'block', 'padding': '10px', 'fontSize': '18px', 'color': '#FFFFFF'}
    active_style = {'display': 'block', 'padding': '10px', 'fontSize': '18px', 'color': '#FFD700'}  # Gold color for active link

    # Change style based on active page
    if pathname == '/about':
        return active_style, inactive_style, inactive_style
    elif pathname == '/overview':
        return inactive_style, active_style, inactive_style
    elif pathname == '/segment':
        return inactive_style, inactive_style, active_style
    else:
        return inactive_style, inactive_style, inactive_style


@app.callback(
    [Output('overview-ridership-graph', 'figure'),
     Output('Overview-kpi-card', 'children'),
     Output('Overview-kpi-yoy-diff', 'children'),
     Output('Overview-kpi-pre-pandemic', 'children'),
     Output('Overview-kpi-pre-pandemic-yoy', 'children')],
    [Input('overview-year-dropdown', 'value')]  # Only need selected_year here
)
def update_content(selected_year):
    # Line chart data: Using full dataset for the trend (2020-2024), ignoring the year filter for the line chart
    trend_data = data[(data['Year'] >= 2020) & (data['Year'] <= 2024)]

    # KPI: Total Ridership for the selected year (in millions)
    filtered_data = data[data['Year'] == selected_year]
    total_ridership = filtered_data['Total Ridership'].sum() / 1_000_000
    previous_year_data = data[data['Year'] == (selected_year - 1)]
    previous_year_ridership = previous_year_data['Total Ridership'].sum() / 1_000_000

    # Calculate YoY difference in ridership (in millions) and YoY percentage change
    yoy_diff = total_ridership - previous_year_ridership
    yoy_ridership_pct = ((total_ridership - previous_year_ridership) / previous_year_ridership) * 100

    # KPI card text and YoY difference with conditional styling
    kpi_text = f"{total_ridership:,.2f}M"
    yoy_text = f"YoY % Change: {yoy_ridership_pct:,.2f}%"
    yoy_color = 'green' if yoy_ridership_pct >= 0 else 'red'

    # KPI: Average Pre-Pandemic Day for the selected year
    avg_pre_pandemic = filtered_data['Subways %'].mean()  # Use a sample mode, e.g., 'Subways'
    previous_year_pre_pandemic = previous_year_data['Subways %'].mean()  # Use the same mode

    # Calculate YoY difference for the pre-pandemic ridership percentage and YoY percentage change
    yoy_pre_pandemic_diff = avg_pre_pandemic - previous_year_pre_pandemic
    yoy_pre_pandemic_pct = ((avg_pre_pandemic - previous_year_pre_pandemic) / previous_year_pre_pandemic) * 100

    # Pre-pandemic KPI card text and YoY difference with conditional styling
    pre_pandemic_text = f"{avg_pre_pandemic:.2f}%"
    yoy_pre_pandemic_text = f"YoY Change: {yoy_pre_pandemic_diff:.2f}%"
    yoy_pre_pandemic_color = 'green' if yoy_pre_pandemic_pct >= 0 else 'red'

    # Line chart figure (display ridership trends for the full range 2020-2024, ignoring the selected year filter)
    fig = px.line(trend_data, x='Date', y='Total Ridership', title=f"Total Ridership Trend (2020 - 2024)")

    return fig, f"{total_ridership:.2f} million", f"{yoy_text}", f"{avg_pre_pandemic:.2f}%", f"YoY Change: {yoy_pre_pandemic_diff:.2f}%"




# Callback for Segment page updates
@app.callback(
    [Output('trend-graph', 'figure'),
     Output('kpi-card', 'children'),
     Output('kpi-yoy-diff', 'children'),
     Output('kpi-pre-pandemic', 'children'),
     Output('kpi-pre-pandemic-yoy', 'children'),
     Output('summary-table', 'data')],
    [Input('mode-dropdown', 'value'), 
     Input('year-dropdown', 'value')]
)
def update_content(selected_mode, selected_year):
    # Filter data for ridership from 2020 to 2024 (ignore year slicer for trend chart)
    trend_data = data[(data['Year'] >= 2020) & (data['Year'] <= 2024)]

    # Ensure there is data for the selected mode and year
    if trend_data.empty:
        return {}, "No data available", "", "", "", []

    # Line chart for daily ridership trend (based only on selected_mode)
    trend_fig = px.line(
        trend_data,
        x='Date',
        y=selected_mode,
        title=f'{selected_mode} Daily Ridership Trend (2020-2024)',
        labels={'Date': 'Date', selected_mode: 'Estimated Ridership'}
    )
    trend_fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title='Date',
        yaxis_title='Ridership',
        xaxis=dict(
            rangeslider=dict(visible=False),
            showline=True,
            showgrid=True,
            gridcolor='lightgrey',
            tickfont=dict(color='black')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgrey',
            tickfont=dict(color='black')
        ),
        title_font=dict(color='black'),
        font=dict(color='black')
    )

    # KPI: Total Ridership for the selected mode in the selected year (in millions)
    filtered_data = data[data['Year'] == selected_year]
    total_ridership = filtered_data[selected_mode].sum() / 1_000_000
    previous_year_data = data[data['Year'] == (selected_year - 1)]
    previous_year_ridership = previous_year_data[selected_mode].sum() / 1_000_000

    # Calculate YoY difference in ridership (in millions) and YoY percentage change
    yoy_diff = total_ridership - previous_year_ridership
    yoy_ridership_pct = ((total_ridership - previous_year_ridership) / previous_year_ridership) * 100

    # KPI card text and YoY difference with conditional styling
    kpi_text = f"{total_ridership:,.2f}M"
    yoy_text = f"YoY % Change: {yoy_ridership_pct:,.2f}%"
    yoy_color = 'green' if yoy_ridership_pct >= 0 else 'red'

    # KPI: Average Pre-Pandemic Day for the selected mode in the selected year
    avg_pre_pandemic = filtered_data[f'{selected_mode} %'].mean()
    previous_year_pre_pandemic = previous_year_data[f'{selected_mode} %'].mean()

    # Calculate YoY difference for the pre-pandemic ridership percentage and YoY percentage change
    yoy_pre_pandemic_diff = avg_pre_pandemic - previous_year_pre_pandemic
    yoy_pre_pandemic_pct = ((avg_pre_pandemic - previous_year_pre_pandemic) / previous_year_pre_pandemic) * 100

    # Pre-pandemic KPI card text and YoY difference with conditional styling
    pre_pandemic_text = f"{avg_pre_pandemic:.2f}%"
    yoy_pre_pandemic_text = f"YoY Change: {yoy_pre_pandemic_diff:.2f}%"
    yoy_pre_pandemic_color = 'green' if yoy_pre_pandemic_pct >= 0 else 'red'

    # Calculate totals for weekday, weekend, Sunday, and overall by year
    yearly_summary = []
    for year in years:
        year_data = data[(data['Year'] == year)]
        weekday_total = year_data[year_data['Day'].isin(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])][selected_mode].sum()
        weekend_total = year_data[year_data['Day'].isin(["Saturday", "Sunday"])][selected_mode].sum()
        sunday_total = year_data[year_data['Day'] == "Sunday"][selected_mode].sum()
        overall_total = year_data[selected_mode].sum()
        yearly_summary.append({
            'Year': year,
            'Weekday': "{:,}".format(weekday_total),
            'Weekend': "{:,}".format(weekend_total),
            'Sunday': "{:,}".format(sunday_total),
            'Total': "{:,}".format(overall_total)
        })

    return (
        trend_fig, 
        kpi_text, 
        html.P(yoy_text, style={'color': yoy_color, 'fontWeight': 'bold', 'fontSize': 16}), 
        pre_pandemic_text,
        html.P(yoy_pre_pandemic_text, style={'color': yoy_pre_pandemic_color, 'fontWeight': 'bold', 'fontSize': 16}), 
        yearly_summary
    )

print("Starting Dash app...")

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8070)
    
