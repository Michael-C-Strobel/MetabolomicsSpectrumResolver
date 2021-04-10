import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import dash_bootstrap_components as dbc

import werkzeug
import requests

from app import app
from views import _get_peaks, _prepare_spectrum, _get_plotting_args
import parsing

dash_app = dash.Dash(name='dashinterface', 
                server=app, url_base_pathname='/dashinterface/',
                external_stylesheets=[dbc.themes.BOOTSTRAP])

NAVBAR = dbc.Navbar(
    children=[
        dbc.NavbarBrand(
            html.Img(src="https://gnps-cytoscape.ucsd.edu/static/img/GNPS_logo.png", width="120px"),
            href="https://gnps.ucsd.edu"
        ),
        dbc.Nav(
            [
                dbc.NavItem(dbc.NavLink("Metabolomics USI - Dash Interface", href="#")),
            ],
        navbar=True)
    ],
    color="light",
    dark=False,
    sticky="top",
)

DATASELECTION_CARD = [
    dbc.CardHeader(html.H5("USI Data Selection")),
    dbc.CardBody(
        [   
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("Spectrum USI", addon_type="prepend"),
                    dbc.Input(id='usi1', placeholder="Enter USI", value=""),
                ],
                className="mb-3",
            ),
            html.Hr(),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("Spectrum USI", addon_type="prepend"),
                    dbc.Input(id='usi2', placeholder="Enter USI", value=""),
                ],
                className="mb-3",
            ),
            html.Hr(),
            html.H4("Drawing Controls"),
        ]
    )
]

LEFT_DASHBOARD = [
    html.Div(
        [
            html.Div(DATASELECTION_CARD),
        ]
    )
]

MIDDLE_DASHBOARD = [
    dbc.CardHeader(html.H5("Data Exploration")),
    dbc.CardBody(
        [
            dcc.Loading(
                id="output",
                children=[html.Div([html.Div(id="loading-output-23")])],
                type="default",
            ),
        ]
    )
]

CONTRIBUTORS_DASHBOARD = [
    dbc.CardHeader(html.H5("Contributors")),
    dbc.CardBody(
        [
            "Mingxun Wang PhD - UC San Diego",
            html.Br(),
            "Wout Bittremieux PhD - UC San Diego",
            html.Br(),
            "Christopher Chen - UC San Diego",
            html.Br(),
            "Simon Rogers PhD - Glasgow",
            html.Br(),
            html.Br(),
            html.H5("Citation"),
            html.A('Bittremieux, Wout, Christopher Chen, Pieter C. Dorrestein, Emma L. Schymanski, Tobias Schulze, Steffen Neumann, Rene Meier, Simon Rogers, and Mingxun Wang. "Universal MS/MS Visualization and Retrieval with the Metabolomics Spectrum Resolver Web Service." bioRxiv (2020).', 
                    href="https://www.biorxiv.org/content/10.1101/2020.05.09.086066v1")
        ]
    )
]

EXAMPLES_DASHBOARD = [
    dbc.CardHeader(html.H5("Examples")),
    dbc.CardBody(
        [
            html.A('Basic', 
                    href=""),
        ]
    )
]

BODY = dbc.Container(
    [
        dcc.Location(id='url', refresh=False),
        dbc.Row([
            dbc.Col([
                dbc.Card(LEFT_DASHBOARD),
                ],
                className="w-50"
            ),
            dbc.Col(
                [
                    dbc.Card(MIDDLE_DASHBOARD),
                    html.Br(),
                    dbc.Card(CONTRIBUTORS_DASHBOARD),
                    html.Br(),
                    dbc.Card(EXAMPLES_DASHBOARD)
                ],
                className="w-50"
            ),
        ], style={"marginTop": 30}),
    ],
    fluid=True,
    className="",
)

dash_app.layout = html.Div(children=[NAVBAR, BODY])

def _get_url_param(param_dict, key, default):
    return param_dict.get(key, [default])[0]

# Callbacks
@dash_app.callback([
                Output('usi1', 'value'), 
                Output('usi2', 'value'), 
              ],
              [Input('url', 'search')])
def determine_task(search):
    try:
        query_dict = urllib.parse.parse_qs(search[1:])
    except:
        query_dict = {}

    usi1 = _get_url_param(query_dict, "usi1", 'mzspec:MSV000082796:KP_108_Positive:scan:1974')
    #usi2 = _get_url_param(query_dict, "usi2", 'mzspec:MSV000082796:KP_108_Positive:scan:1977')
    usi2 = _get_url_param(query_dict, "usi2", '')

    return [usi1, usi2]


def _process_single_usi(usi, plotting_args):
    spectrum, source_link, splash_key = parsing.parse_usi(usi)
    spectrum = _prepare_spectrum(spectrum, **plotting_args)

    usi1_url = "/svg/?usi={}".format(usi)
    local_url = "http://localhost:5000{}".format(usi1_url)
    r = requests.get(local_url)

    image_obj = html.Img(src=usi1_url)

    json_button = html.A(dbc.Button("Download as JSON", color="primary", className="mr-1"), href="/json/?usi1={}".format(usi))
    csv_button = html.A(dbc.Button("Download as CSV", color="primary", className="mr-1"), href="/csv/?usi1={}".format(usi))
    png_button = html.A(dbc.Button("Download as PNG", color="primary", className="mr-1"), href="/png/?usi1={}".format(usi), download="spectrum.png")
    svg_button = html.A(dbc.Button("Download as SVG", color="primary", className="mr-1"), href=usi1_url, download="spectrum.svg")
    download_div = html.Div([
        json_button,
        csv_button,
        png_button,
        svg_button,
    ])


    peak_annotations = spectrum.annotation.nonzero()[0].tolist()
    peaks_list = _get_peaks(spectrum)

    return [[image_obj, html.Br(), download_div, str(peak_annotations)]]


@dash_app.callback([
                Output('output', 'children')
              ],
              [
                  Input('usi1', 'value'),
                  Input('usi2', 'value'),
              ],
              [
                  
              ])
def draw_figure(usi1, usi2):
    if len(usi1) > 0 and len(usi2) > 0:
        mirror_url = "/svg/mirror/?usi1={}&usi2={}".format(usi1, usi2)
        local_url = "http://localhost:5000{}".format(mirror_url)
        r = requests.get(local_url)

        image_obj = html.Img(src=mirror_url)

        json_button = html.A(dbc.Button("Download as JSON", color="primary", className="mr-1"), href="/json/mirror?usi1={}&usi2={}".format(usi1, usi2))
        png_button = html.A(dbc.Button("Download as PNG", color="primary", className="mr-1"), href="/png/mirror?usi1={}&usi2={}".format(usi1, usi2), download="mirror.png")
        svg_button = html.A(dbc.Button("Download as SVG", color="primary", className="mr-1"), href=mirror_url, download="mirror.svg")
        download_div = html.Div([
            json_button,
            png_button,
            svg_button,
        ])
        

        return [[image_obj, html.Br(), download_div]]
    else:
        plotting_args = _get_plotting_args(werkzeug.datastructures.ImmutableMultiDict())
        return _process_single_usi(usi1, plotting_args)




if __name__ == "__main__":
    dash_app.run_server(debug=True, port=5000, host="0.0.0.0")