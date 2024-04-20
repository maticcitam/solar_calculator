'''
PROJECT 3
Author: Matic Robnik
Date: April 2024
The objective is to make a dashboard that estimates the performance of the specified photovoltaic system. This is a python script creating the frontend part of application. For backend calculations and loading of data see file 'backend.py'. Custom stylesheet is saved in file 'assets/style.css'.
'''

from backend import *
from dash_bootstrap_templates import load_figure_template
load_figure_template(["darkly"])

from dash_extensions.javascript import assign
from dash import Dash, Output, Input, html
from dash import dcc
import dash
from dash_leaflet import Map, TileLayer
import plotly.express as px
import plotly.graph_objs as go

eventHandlers = dict(
    click=assign("function(e, ctx){ctx.setProps({click_lat_lng: [e.latlng.lat, e.latlng.lng]})}")
)

panel_cost = 300 # cost of 1 m^2 of PV panel in EUR
electricity_cost = 0.18 # cost of 1 kWh in EUR 
input_data = dict()

app = Dash()
app.layout = html.Div([
    html.Div([
        html.Div(style={'position': 'absolute', 'top': 0, 'left': 0, 'right': 0, 'bottom': 0, 'background-image': 'url("/assets/header.png")', 'background-size': 'cover', 'opacity': '0.3'}),
        html.Div([
            html.H1("Solar Power Costs & Savings Calculator", style={'color': 'white', 'font-size': '48px'}),
        ], style={'position': 'absolute', 'top': '85%', 'left': '40%', 'transform': 'translate(-50%, -50%)', 'width': '100%', 'padding': '20px'}),
    ], style={'padding': '2px', 'height': '200px', 'position': 'relative'}),

    html.Br(),
    html.Div('Estimate the costs and potential savings associated with installing your Photovoltaic system. Choose the specifications of your PV system, input your average electricity consumption, and let us calculate the expected performance of your solar panel.'),
    html.Br(),
    html.H3('1. Where in the world do you plan to set up your PV system? Click on the map or insert the coordinates.'),
    html.Br(),
    Map(children=[TileLayer()], eventHandlers=eventHandlers,
        style={'height': '50vh'}, center=[46, 14.3], zoom=6, id='map'),
    html.Div([
        html.P("Latitude"),
        dcc.Input(id="latitude-input", type="number", step="any", value=46, className='custom-input'),
        html.P("Longitude"),
        dcc.Input(id="longitude-input", type="number", step="any", value=14.3, className='custom-input'),
    ], style={'margin': '10px'}),
    html.Br(),
    html.H3('2. Properties of the PV system and installation site:'),
        html.Div([
        html.P("Installation type"),
        dcc.Dropdown(
            id="mounting-dropdown",
            options=[
                {'label': 'Roof mounted', 'value': 'building'},
                {'label': 'Free standing', 'value': 'free'},
            ],
            value='South',
            className='custom-dropdown',
        )
    ]),
    html.Div([
        html.P("Area (in m^2)"),
        dcc.Input(id="area-input", type="number", value=10, className='custom-input')
    ]),
    html.Div([
        html.P("Tilt (angle in degrees)"),
        dcc.Input(id="tilt-input", type="number", value=30, className='custom-input')
    ]),
    html.Div([
        html.P("Orientation"),
        dcc.Dropdown(
            id="orientation-dropdown",
            options=[
                {'label': 'North', 'value': 0},
                {'label': 'East', 'value': 90},
                {'label': 'South', 'value': 180},
                {'label': 'West', 'value': 270},
                {'label': 'Northeast', 'value': 45},
                {'label': 'Northwest', 'value': 315},
                {'label': 'Southeast', 'value': 135},
                {'label': 'Southwest', 'value': 225},
            ],
            value='South',
            className='custom-dropdown',
        )
    ]),
    html.Div([
        html.P("System capacity, peak power (in kW)"),
        dcc.Input(id="peakpower-input", type="number", value=1, className='custom-input')
    ]),
    html.Br(),
    html.H3('3. What is your current power consumption?'),
    html.P('This number will help us compare how much energy your PV system generates with how much you use. To figure out your current energy use, just add up all your electricity bills from the past year. If you\'re planning to switch from other energy sources to electricity, remember to include those in your calculation too.'),
    html.Div([
        html.P("Yearly power consumption (in kWh)"),
        dcc.Input(id="power-input", type="number", value=20000, className='custom-input')
    ]),
    html.Br(),
    html.P('To estimate the performance of your PV system, click the button below. It might take a while, take it easy 😎'),
    html.Button(html.H3('Calculate Costs & Savings'), id='calc-button', className='custom-button'),
    dcc.Loading(
            id="loading-1",
            type="default",
            children=html.Div(id="results")
        ),

    # Footer
    html.Footer(className="footer", children=[
        html.Div(className="footer-content", children=[
            html.Div(className="footer-text", children=[
                html.P('This calculator was developed as part of a project for the Energy Services course at Instituto Superior Técnico, Lisbon.'),
                html.P('The dashboard and calculations were created by Matic Robnik under the mentorship of Professor Carlos Santos Silva.'),
            ]),
            html.Img(className="footer-image", src="/assets/footer.jpg"),
        ]),
    ])

    ], style={'position': 'relative'})


@app.callback(Output("map", "viewport"), 
              [Input("latitude-input", "value"),
               Input("longitude-input", "value")],
              prevent_initial_call=True)
def fly_to_location(latitude, longitude):
    input_data['latitude'], input_data['longitude'] = latitude, longitude
    return dict(center=[latitude, longitude], zoom=10, transition="flyTo")

@app.callback([Output("latitude-input", "value"), Output("longitude-input", "value")], 
              Input("map", "click_lat_lng"),
              prevent_initial_call=True)
def click_on_the_map(click_lat_lng):
    if click_lat_lng:
        return [click_lat_lng[0], click_lat_lng[1]]

@app.callback(Output('results', 'children'),
              Input("calc-button", 'n_clicks'),
              [Input("area-input", "value"),
               Input("tilt-input", "value"),
               Input("mounting-dropdown", "value"),
               Input("orientation-dropdown", "value"),
               Input("peakpower-input", "value"),
               Input("power-input", "value")],
              prevent_initial_call=True)
def calculate_everything(n_clicks, area, tilt, mounting, orientation, peakpower, power):
    triggered_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if triggered_id == 'calc-button':
        input_data['area'], input_data['tilt'], input_data['mountingplace'], input_data['orientation'], input_data['peakpower'], input_data['power'] = area, tilt, mounting, orientation, peakpower, power
        avg_power, std_power, avg_yearly, error_yearly, data = calculate_avg_power(input_data['latitude'], 
                                                                                   input_data['longitude'],
                                                                                   input_data['peakpower'], 
                                                                                   input_data['tilt'], 
                                                                                   input_data['orientation'],
                                                                                   input_data['mountingplace'])
        yearly_production = avg_yearly * input_data['area']
        yearly_production_error = error_yearly * input_data['area']
        independence = yearly_production / input_data['power']
        investment = input_data['area'] * panel_cost
        payback_period = investment / (min(input_data['power'], yearly_production) * electricity_cost)

        date_range = np.array(pd.date_range(start='2024-01-01', end='2024-12-31', freq='h'))
        trace_main = go.Scatter(x=date_range,y=avg_power,mode='lines',name='Average Power', line=dict(color='red'),)
        trace_fill = go.Scatter(
            x=np.concatenate([date_range, date_range[::-1]]),  # Concatenate x with its reverse to create a closed loop for fill
            y=np.concatenate([avg_power+std_power, (avg_power-std_power)[::-1]]),
            fill='toself',
            fillcolor='rgba(0, 176, 246, 0.3)',
            line=dict(color='rgba(0, 176, 246,0)'),
            name='Standard Deviation'
        )
        layout = go.Layout(
            yaxis=dict(
                title='Produced Power [W]'
            ),
            title='Power Production of the PV system over the year'
        )
        fig = go.Figure(data=[trace_main, trace_fill], layout=layout)

        return [html.H1('Results of our calculations for your Photovoltaic system'),
                html.Br(),
                html.Div([
                    html.H3([f'Average yearly electricity production: ', html.Span(f'{yearly_production:.0f} ± {yearly_production_error:.0f} kWh', style={'color': 'lightblue', 'font-weight': 'bold'})]),
                    html.H3([f'Level of energetic independence: ', html.Span(f'{(100 * independence):.0f}%', style={'color': 'lightblue', 'font-weight': 'bold'})]),
                    html.H3([f'Expected cost of investment: ', html.Span(f'{investment:.2f} EUR', style={'color': 'lightblue', 'font-weight': 'bold'})]),
                    html.H3([f'Payback period of the investment: ', html.Span(f'{payback_period:.1f} years', style={'color': 'lightblue', 'font-weight': 'bold'})]),
                ], style={'background-color': '#395e85', 'padding': '10px'}),
                html.Br(),
                dcc.Graph(id='electricity-production-plot', figure=fig),
                html.Br(),
                html.Span('Note: The solar irradiation data for the chosen location, along with other parameters, was obtained from the PVGIS database. Power production calculations were conducted using models from the `pvlib.iotools` library and averaged over three years (the number of years considered is limited due to computational time constraints). The cost of solar panels can vary significantly. For our calculations, we\'ve assumed an average cost of 300 euros per square meter of solar panel. Similarly, we\'ve estimated the electricity price at 18 cents per kilowatt-hour (kWh). Additionally, our calculations do not account for the potential sale of surplus electricity. It\'s essential to note that specific systems may necessitate more precise definitions, potentially leading to significantly different power outputs. These calculations are intended for informational purposes only.', style={'color': 'gray', 'opacity': '0.5'}),
                ]

    return ''


if __name__ == '__main__':
    app.run_server(debug=False, host="0.0.0.0", port=10000)
    # from waitress import serve
    # serve(app, host="0.0.0.0", port=8050)