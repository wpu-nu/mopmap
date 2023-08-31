from dash_extensions.javascript import assign
from pprint import pprint 
from dash import Dash, ctx
import dash_leaflet as dl
from pathlib import Path
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL, MATCH
from dash.exceptions import PreventUpdate
from dash import dcc
from dash import html
from datetime import datetime, timedelta
import json

def bp():
  from pudb import set_trace; set_trace()


t0 = datetime(1986, 3, 1, 0, 0, 0)

timemarks={}
for i in range(-7, +7):
    t = t0 + timedelta(days=i)
    timemarks[int((t-t0).total_seconds())] = t.date().isoformat()

#t = datetime(1986, 2, 28, 23, 21, 20)
#timemarks[int((t-t0).total_seconds())] = "Skotten"


pprint(timemarks)

time_slider_min = -100
time_slider_max = 500
center_pos = [59.33662248750816, 18.06278754091279]

actors = {
            "LEN": {
                "color": "#DD3333",
                "positions": {
                        0: [59.33662248750816, 18.06278754091279],
                },
            },
            "SE": { 
                "color": "#1133FF",
                "positions": {
                        0: [59.32662248750816, 18.16278754091279],
                }}
        }

def get_position_at(delta_t, actor):
    
    #print(f"delta_t: >{delta_t}<")
    #print(f"actor: >{actor}<")


    if len(actor) == 0:
        return center_pos

    if len(actor) == 1:
        return list(actor.values())[0]

    delta_t = int(delta_t)

    if delta_t in actor.keys():
        return actor[delta_t]

    if delta_t <= min(actor.keys()):
        return actor[min(actor.keys())]

    if delta_t >= max(actor.keys()):
        return actor[max(actor.keys())]


    ls = min(actor.keys())
    for dt0 in sorted(actor.keys()):
        if dt0 < delta_t:
            ls = dt0
            continue
        break

    le = sorted(actor.keys())[1]
    for dt0 in sorted(actor.keys()):
        if dt0 < delta_t:
            continue
        le = dt0
        break

    #print(ls, le)

    fraction = (delta_t - ls) / (le - ls)

    #print(fraction)

    ps = actor[ls]
    pe = actor[le]


    return [ps[0] + fraction * (pe[0] - ps[0]), ps[1] + fraction * (pe[1] - ps[1])]

markerEventHandlers = dict(move=assign("function(e, ctx){ctx.setProps({actor: e.target.options.id, moveend: [e.latlng.lat, e.latlng.lng]})}"))

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])

app.layout = dbc.Container(
    className="dbc",
    children=[
    dcc.Store(id='local-store', storage_type='local'),
    dbc.Row(    className="dbc", children=[
        dl.Map(
            id="dl-widget", 
            attributionControl=False,
            style={'height': '80vh'}, 
            center=center_pos, 
            zoom=18
            )
    ]),
    dbc.Row([
            html.Div(
              id="state-display",
              className="text-md-center"
              # style={
              #   #"backgroundColor": "#E5EFE5",
              #   #"borderColor": "black",
              #   #"borderStyle": "solid",
              #   #"borderWidth": "1px",
              #   "height": "4vh",
              #   "margin": "0px",
              #   "paddingLeft": "8px",
              #   "paddingRight": "0px",
              #   "paddingTop": "8px",
              #   "paddingBottom": "10px",
              #   "width": "auto",
              #   "textAlign": "center"
              #   }
            ),
    ]),
    dbc.Row([
                dcc.Slider(id="time-point-slider",
                           min=time_slider_min,
                           max=time_slider_max,
                           value=0,
                           step=1,
                           className="mb-2",
                           updatemode='drag',
                           dots=False,
                           marks=timemarks,
                           included=False
                           #tooltip={"placement": "bottom", "always_visible": True},
                )
            ],
            style={'height': '4vh'}
    ),
    dbc.Row([
        dcc.RangeSlider(
            id="time-zoom-slider",
            min= -60 * 60 * 24 * 7,
            max= +60 * 60 * 24 * 7,
            step=1,
            marks=timemarks,
            value=[-60 * 60 * 24 * 1, 60 * 60 * 24 * 1]
        )           
    ]),
    dbc.Row([
        dbc.Col([
            html.Button('Spara', id='save-positions-btn', n_clicks=0),
        ]),
        dbc.Col([
            html.Button('Ny aktör', id='new-actor-modal-open-btn', n_clicks=0),
        ]),
    ]),
    dbc.Modal(
        [
            dbc.ModalHeader(id="new-actor-modal-header"),
            dbc.ModalBody(
                [
                "Lägg till en ny aktör. Använd en förkortning på max 4 bokstäver.",
                dbc.Input(
                    type="text",
                    id="new-actor-name-input",
                    placeholder="OP",
                ),
                dbc.Input(
                    type="color",
                    id="new-actor-modal-color",
                    value="#880000",
                    style={"width": 75, "height": 50},
                ),
                ]
            ),

            dbc.ModalFooter([dbc.Button("Avbryt", id="new-actor-modal-close"), dbc.Button("Skapa", id="new-actor-save-btn")]),
        ],
        id="new-actor-modal",
        is_open=False
    ),    

])


@app.callback(
    Output("new-actor-modal", "is_open"),
    Input("new-actor-modal-open-btn", "n_clicks"),
    Input("new-actor-modal-close", "n_clicks"),
    Input("new-actor-save-btn", 'n_clicks'))
def open_new_actor_modal(n_clicks_open, n_clicks_close, n_clicks_save):



    if len(ctx.triggered) > 1 or (len(ctx.triggered) == 1 and ctx.triggered[0]['value'] == 0):
        raise PreventUpdate
    
    if ctx.triggered_id == 'new-actor-modal-close':
        return False

    if ctx.triggered_id == 'new-actor-save-btn':
        return False

    if ctx.triggered_id == 'new-actor-modal-open-btn':
        return True

    return False



@app.callback(
    Output("dl-widget", "children"),
    Output("state-display", "children"),
    Input("time-point-slider", "value"),
    Input("local-store", "modified_timestamp"),
    Input("new-actor-save-btn", 'n_clicks'),
    State("local-store", "data"))
def display_map(delta_t, mtime, n_clicks_save, data):
    
    if delta_t is None:
        raise PreventUpdate

    global t0
    t = t0 + timedelta(seconds=delta_t)
    



    if not data:
        data = actors
        print("Loaded default data")
    else:
        for actor in data.keys():
            data[actor]["positions"] = {int(k):v for k,v in data[actor]["positions"].items()}
    
    
    mapch = [
        dl.TileLayer(
            id="tile-layer", 
            maxNativeZoom=22, 
            maxZoom=22, 
            minZoom=5
        )
    ]
    idx=0

    for actor_name in data:
        actor_color = data[actor_name]["color"]
        icon = dict(
                html=f"<div style=\"background-color: {actor_color}A0;\">{actor_name}</div>",
                className='marker-standard',
                iconSize=[30, 30],
                iconAnchor=[20,20]
        )

        mapch.append(
            dl.Polyline(
                id=f"actor-trajectory-{actor_name}", 
                positions=[data[actor_name]["positions"][p] for p in sorted(data[actor_name]["positions"].keys())],
                color=actor_color
            )
        )

        mapch.append(
            dl.DivMarker(
                id={"role": "actor-marker", "name": actor_name},
                position=get_position_at(delta_t, data[actor_name]["positions"]), 
                iconOptions=icon, 
                draggable=True,
                eventHandlers=markerEventHandlers
                #interactive=True
                )
            )
        idx += 1

    
    return [mapch, t.isoformat(sep=" ")]




@app.callback(
        Output("time-point-slider", "min"), 
        Output("time-point-slider", "max"), 
        Input("time-zoom-slider", "value"))
def update_slider_range(values):
    print(values)
    return values




@app.callback(
        Output("local-store", "data"), 
        Input("save-positions-btn", 'n_clicks'),
        Input("new-actor-save-btn", 'n_clicks'),
        [
            State("time-point-slider", "value"),
            State({'role': 'actor-marker', "name": ALL}, 'moveend'),
            State({'role': 'actor-marker', "name": ALL}, 'actor'),
            State("new-actor-name-input", "value"),
            State("new-actor-modal-color", "value"),
            State("local-store", "data")
            
        ])
def save_positions_at_timestamp(n_clicks_save_pos, n_clicks_save_new, delta_t, moveend, moveactor, new_actor_name, new_actor_color, data):

    global actors


    triggered = ctx.triggered

    if len(triggered) > 1 or (len(triggered) == 1 and triggered[0]['value'] == 0):
        raise PreventUpdate
    
    if n_clicks_save_pos is None or delta_t is None:
        raise PreventUpdate
    
    if ctx.triggered_id == "new-actor-save-btn":
        data[new_actor_name] = {
                "positions": {delta_t:center_pos},
                "color": new_actor_color,
            }
        return data

    
    if not data:
        data = actors
    else:
        for actor in data.keys():
            data[actor]["positions"] = {int(k):v for k,v in data[actor]["positions"].items()}


    
    for actor, position in zip(moveactor, moveend):
        if actor is None or position is None:
            continue
        
        actor_data = json.loads(actor)
        data[actor_data["name"]]["positions"][delta_t] = position
        

    #pprint(data)

    return data





if __name__ == '__main__':
    app.run(host='10.0.0.40',
            #threaded=True,
            port='8080',
            debug=True)

