
import flask
import json
from datetime import datetime, timedelta, date
from pathlib import Path
from pprint import pprint 



from dash import Dash, ctx, dcc, html
import dash_leaflet as dl
import dash_mantine_components as dmc
import dash_player

from dash.dependencies import Input, Output, State, ALL, MATCH
from dash.exceptions import PreventUpdate
from dash_extensions.javascript import assign
from dash_iconify import DashIconify



def bp():
  from pudb import set_trace; set_trace()


t0 = datetime(1986, 3, 1, 0, 0, 0)
days_before=2
days_after=2
date_marks=[]
for i in range(-days_before, +days_after):
    t = t0 + timedelta(days=i)
    date_marks.append({
            "value": int((t-t0).total_seconds()),
            "label": t.date().isoformat()
            })

#pprint(date_marks)


hour_marks=[]
for i in range(-days_before * 24, +days_after * 24):
    t = t0 + timedelta(hours=i)
    hour_marks.append({
            "value": int((t-t0).total_seconds()),
            "label": t.time().isoformat()
            })

#pprint(hour_marks)


minute_marks=[]
for i in range(-days_before * 24, +days_after * 24):
    t = t0 + timedelta(minutes=i)
    minute_marks.append({
            "value": int((t-t0).total_seconds()),
            "label": t.time().isoformat()
            })

#pprint(minute_marks)



#t = datetime(1986, 2, 28, 23, 21, 20)
# date_marks.append({
#     "value": int((t-t0).total_seconds()),
#     "label": "Skotten"
# })




time_slider_min = -100000
time_slider_max = 50000
center_pos = [59.33662248750816, 18.06278754091279]

actors = {
             # "OP": {
            # type: "actor", 
             #     "color": "#FF1111",

             #     "positions": {
             #             0: [59.33662248750816, 18.06278754091279],
             #     }
             # },
#             "SE": { 
# type: "actor", 
#                 "color": "#1133FF",
#                 "positions": {
#                         0: [59.32662248750816, 18.16278754091279],
#                 }}
}

#dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
server = flask.Flask(__name__) # define flask app.server
#app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css], server=server)

app = Dash(
    __name__,
    #external_stylesheets=[
        # include google fonts
    #    "https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;900&display=swap"
    #],
)


def get_position_at(delta_t, actor, default_position=None):
    
    #print(f"delta_t: >{delta_t}<")
    #print(f"actor: >{actor}<")


    if len(actor) == 0:
        return center_pos

    if len(actor) == 1:
        return list(actor.values())[0]

    delta_t = int(delta_t)

    if delta_t in actor.keys():
        return actor[delta_t]

    if delta_t < min(actor.keys()):
        if default_position:
            return default_position
        return actor[min(actor.keys())]

    if delta_t >= max(actor.keys()):
        if default_position:
            return default_position
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

markerEventHandlers = dict(
    move=assign("function(e, ctx){ctx.setProps({actor: e.target.options.id, moveend: [e.latlng.lat, e.latlng.lng]})}")
)
pointEventHandlers = dict(    
    click=assign("function(e, ctx){ctx.setProps({actor: e.target.options.id, n_clicks: (ctx.n_clicks == undefined ? 1 : ctx.n_clicks + 1)})}")
)




app.layout = dmc.MantineProvider(
    children=[
        dcc.Store(id='local-store', storage_type='local'),
        dmc.Container(
            #style={"width": "95%"},
            fluid=True,
            m=0,
            p=0,
            children=[
                dl.Map(
                    children=[dl.TileLayer()],
                    id="dl-widget", 
                    attributionControl=False,
                    style={'height': '65vh'}, 
                    center=center_pos, 
                    zoom=18
                )
            ]
        ),

        dmc.Space(h="lg"),
        dmc.Center(
            dmc.Group(
                m="0",
                p="0",
                children=[
                dmc.ActionIcon(
                    DashIconify(icon="bi:chevron-bar-left", width=20),
                    size="lg",
                    variant="outline",
                    id="step-prev",
                ),
                dmc.ActionIcon(
                    DashIconify(icon="bi:chevron-double-left", width=20),
                    size="lg",
                    variant="outline",
                    id="step-back-h",

                ),
                dmc.ActionIcon(
                    DashIconify(icon="bi:chevron-left", width=20),
                    size="lg",
                    variant="outline",
                    id="step-back-m",
                ),
                dmc.ActionIcon(
                    DashIconify(icon="bi:chevron-compact-left", width=20),
                    size="lg",
                    variant="outline",
                    id="step-back-s",
                ),
                dmc.TimeInput(
                    id="time-picker",
                    withSeconds=True,
                    value=datetime(1986, 3, 1, 0, 0, 0),
                    size="sm"
                ),

                dmc.ActionIcon(
                    DashIconify(icon="bi:chevron-compact-right", width=20),
                    size="lg",
                    variant="outline",
                    id="step-forward-s",
                ),
                dmc.ActionIcon(
                    DashIconify(icon="bi:chevron-right", width=20),
                    size="lg",
                    variant="outline",
                    id="step-forward-m",
                ),
                dmc.ActionIcon(
                    DashIconify(icon="bi:chevron-double-right", width=20),
                    size="lg",
                    variant="outline",
                    id="step-forward-h",
                ),
                dmc.ActionIcon(
                    DashIconify(icon="bi:chevron-bar-right", width=20),
                    size="lg",
                    variant="outline",
                    id="step-next",
                ),
            ])
        ),
        dmc.Space(h='md'),
        dmc.Center(
            dmc.Group([
                
                dmc.ActionIcon(
                    DashIconify(icon="bi:caret-left", width=20),
                    size="lg",
                    variant="outline",
                    id="step-back-d",
                ),
        
                dmc.DatePicker(
                    id="date-picker",
                    value=date(1986, 3, 1),
                    size="sm",
                    inputFormat="YYYY-MM-DD"
                ),
              dmc.ActionIcon(
                    DashIconify(icon="bi:caret-right", width=20),
                    size="lg",
                    variant="outline",
                    id="step-forward-d",
                ),
            ])
        ),
        
        
        dmc.Space(h='lg'),
        dmc.Divider(label="Tidslinje", labelPosition="center", variant="dashed", ml=35, mr=35),
        dmc.Space(h='lg'),
        dmc.Slider(
            id="time-point-slider",
             min=time_slider_min,
             max=time_slider_max,
             value=0,
             step=1,
             updatemode='drag',
             marks=date_marks,
             ml=35,
             mr=35,
             w="95%",
             size=2,
             thumbSize=25,
             labelAlwaysOn=False,
             thumbChildren=[DashIconify(icon="bi:caret-up", width=25)]
            
        ),
        dmc.Space(h='xl'),
        dmc.Space(h='xl'),
        dmc.Divider(label="Zoom", labelPosition="center", variant="dashed", ml=35, mr=35),
        dmc.Space(h='lg'),
        dmc.RangeSlider(
              id="time-zoom-slider",
              min= -60 * 60 * 24 * days_before,
              max= +60 * 60 * 24 * days_after,
              step=60,
              marks=date_marks,
              value=[-60 * 60 * 24 * 1, 60 * 60 * 24 * 1],
              size=2,
              thumbSize=25,
              ml=35,
              mr=35,
              w="95%",
              labelAlwaysOn=False,
              thumbChildren=[DashIconify(icon="bi:chevron-right", width=25), DashIconify(icon="bi:chevron-left", width=25)]

        ),
        dmc.Space(h='xl'),
        #dmc.Divider(label="Zoom", labelPosition="center", variant="dashed"),
        dmc.Space(h='lg'),
        dmc.Center(
            children=[
                dmc.Button(
                    "Ny aktör",
                    id="new-actor-modal-open-btn",
                    variant="outline",
                    size="xs",
                    rightIcon=DashIconify(icon="fa6-solid:person-rays", width=20)
                ),
                dmc.Button(
                    "Ta bort",
                    id="delete-actor-btn",
                    variant="red",
                    size="xs",
                    color="red",
                    disabled=True,
                    rightIcon=DashIconify(icon="fa6-solid:person-circle-xmark", width=20)
                ),
                dmc.Button(
                    "Ny händelse",
                    id="new-event-modal-open-btn",
                    variant="outline",
                    size="xs",
                    rightIcon=DashIconify(icon="bi:broadcast", width=20)
                ),
                dmc.Button(
                    "Spara positioner",
                    id='save-positions-btn',
                    variant="outline",
                    size="xs",
                    rightIcon=DashIconify(icon="tabler:map-up", width=20)
                ),
                dmc.Button(
                    children=["Tyst"],
                    id='toggle-mute',
                    variant="outline",
                    size="xs",
                    rightIcon=DashIconify(icon="bi:volume-up", width=20),
                ),
            ]

        ),


        # New actor
        dmc.Modal(
            id="new-actor-modal",
            title="Lägg till en ny aktör",
            zIndex=10000,
            children=[
                    dmc.Text("Använd en förkortning på max 4 bokstäver."),
                    dmc.TextInput(
                        type="text",
                        id="new-actor-name-input",
                        placeholder="OP",
                    ),
                    dmc.Space(h=20),
                    dmc.Text("Välj aktörens färg."),
                    dmc.ColorPicker(
                         id="new-actor-modal-color",
                         value="#880000",
                         format="hex"
                    ),
                    dmc.Space(h=20),
                    dmc.Divider(),
                    dmc.Space(h=20),
                    dmc.Group([
                        
                        dmc.Button(
                            "Close",
                            color="red",
                            variant="outline",
                            id="new-actor-modal-close",
                        ),
                        dmc.Button("Skapa", id="new-actor-save-btn", rightIcon=DashIconify(icon="fa6-solid:person-rays", width=20)),
                    ],
                    position="right",
                ),
            ],
            opened=False
        ),    


        # New event
        dmc.Modal(
            id="new-event-modal",
            title="Lägg till en ny händelse",
            zIndex=10000,
            children=[
                    dmc.Text("Använd en förkortning på max 4 bokstäver."),
                    dmc.TextInput(
                        type="text",
                        id="new-event-name-input",
                        placeholder="LACa",
                    ),
                    dmc.Space(h=20),
                    dmc.Text("Välj händelsens färg."),
                    dmc.ColorPicker(
                         id="new-event-modal-color",
                         value="#008800",
                         format="hex"
                    ),
                    dmc.Space(h=20),
                    dmc.Divider(),
                    dmc.Space(h=20),
                    dmc.Group([
                        dmc.Button(
                            "Close",
                            color="red",
                            variant="outline",
                            id="new-event-modal-close",
                        ),
                        dmc.Button("Skapa", id="new-event-save-btn", rightIcon=DashIconify(icon="bi:broadcast", width=20)),
                    ],
                    position="right",
                ),
            ],
            opened=False
        ),    

        html.Div(id='clicked-marker', style={'display': 'hidden'}, children = ""),
])

@app.callback(
    Output('toggle-mute', 'rightIcon'),
    Output('toggle-mute', 'children'),
    Input('toggle-mute', 'n_clicks')
    )
def toggle_sound(n_clicks):
    if n_clicks and n_clicks % 2:
        return [DashIconify(icon="bi:volume-up", width=20), "Ljud"]

    return [DashIconify(icon="bi:volume-mute", width=20), "Tyst"]


@app.callback(
    Output("new-actor-modal", "opened"),
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
    Output("new-event-modal", "opened"),
    Input("new-event-modal-open-btn", "n_clicks"),
    Input("new-event-modal-close", "n_clicks"),
    Input("new-event-save-btn", 'n_clicks'))
def open_new_event_modal(n_clicks_open, n_clicks_close, n_clicks_save):

    if len(ctx.triggered) > 1 or (len(ctx.triggered) == 1 and ctx.triggered[0]['value'] == 0):
        raise PreventUpdate
    
    if ctx.triggered_id == 'new-event-modal-close':
        return False

    if ctx.triggered_id == 'new-event-save-btn':
        return False

    if ctx.triggered_id == 'new-event-modal-open-btn':
        return True

    return False



# Cycle Found: time-point-slider.value -> time-picker.value -> time-point-slider.value

@app.callback(
    Output("time-point-slider", "value"),
    Input("step-forward-s", "n_clicks"),
    Input("step-forward-m", "n_clicks"),
    Input("step-forward-h", "n_clicks"),
    Input("step-forward-d", "n_clicks"),
    Input("step-next", "n_clicks"),
    Input("step-back-s", "n_clicks"),
    Input("step-back-m", "n_clicks"),
    Input("step-back-h", "n_clicks"),    
    Input("step-back-d", "n_clicks"),    
    Input("step-prev", "n_clicks"),    
    State("time-point-slider", "value"),
    State("clicked-marker", "children"),
    State("local-store", "data"))
def step_slider(fs, fm, fh, fd, sn, bs, bm, bh, bd, sp, slider_val, clicked_marker, data):
  
    if slider_val is None:
        slider_val = 0

    if ctx.triggered_id == "step-forward-s":
        return slider_val + 1
    elif ctx.triggered_id == "step-forward-m":
        return slider_val + 60
    elif ctx.triggered_id == "step-forward-h":
        return slider_val + 60 * 60
    elif ctx.triggered_id == "step-forward-d":
        return slider_val + 60 * 60 * 24
    
    elif ctx.triggered_id == "step-next":
        print("step-next")
        if clicked_marker in data.keys():
            for i in sorted([int(i) for i in data[clicked_marker]["positions"].keys()], reverse=False):
                print(i, slider_val)
                if int(i) > slider_val:
                    return int(i)
        raise PreventUpdate


    if ctx.triggered_id == "step-back-s":
        return slider_val - 1
    elif ctx.triggered_id == "step-back-m":
        return slider_val - 60
    elif ctx.triggered_id == "step-back-h":
        return slider_val - 60 * 60
    elif ctx.triggered_id == "step-back-d":
        return slider_val - 60 * 60 * 24


    elif ctx.triggered_id == "step-prev":
        print("step-prev")
        if clicked_marker in data.keys():
            for i in sorted([int(i) for i in data[clicked_marker]["positions"].keys()], reverse=True):
                if int(i) < slider_val:
                    return int(i)
        raise PreventUpdate

    # if ctx.triggered_id in ["date-picker", "time-picker"]:
    #     print("update_slider")
    #     print(time_entered)
    #     print(date_entered)
    #     d = date_entered
    #     return 1000




@app.callback(
        Output("clicked-marker", "children"),
        Input({'role': 'actor-trajectory-point', "name": ALL}, 'n_clicks'),
        Input({'role': 'actor-marker', "name": ALL}, 'n_clicks'),
        State({'role': 'actor-marker', "name": ALL}, 'actor'))
def on_marker_click(n_clicks_point, n_clicks_marker, actor):
    #print(n_clicks_point)
    if len(ctx.triggered) > 1 or (len(ctx.triggered) == 1 and ctx.triggered[0]['value'] == 0) or ctx.triggered[0]["prop_id"] == ".":
        raise PreventUpdate

    actor = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    return actor["name"]



@app.callback(
    Output("dl-widget", "children"),
    Output("time-picker", "value"),
    Output("date-picker", "value"),
    Output("time-zoom-slider", "value"),    
    Output("delete-actor-btn", "disabled"),
    Input("time-point-slider", "value"),
    Input("local-store", "modified_timestamp"),
    Input("clicked-marker", "children"),
    State('toggle-mute', 'children'),
    State("local-store", "data"),
    State({'role': 'actor-marker', "name": ALL}, 'moveend'),
    State({'role': 'actor-marker', "name": ALL}, 'actor'),
    State("time-zoom-slider", "value"))
def display_map(delta_t, mtime, clicked_marker, mute, data, moveend, moveactor, time_zoom):
    
    if delta_t is None:
        delta_t = 0

    global t0
    print(t0)
    t = t0 + timedelta(seconds=delta_t)
    print(t)

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

    
    default_positions = {}
    for actor, position in zip(moveactor, moveend):
        if actor is None or position is None:
            continue
        
        actor_data = json.loads(actor)
        default_positions[actor_data["name"]] = position
    

    delete_actor_disabled = True
    for actor_name in data:
        
        actor_color = data[actor_name]["color"]
        actor_type = data[actor_name].get("type", "actor")
        transperancy = "FF" if clicked_marker == actor_name else "99"
        actor_path=[data[actor_name]["positions"][p] for p in sorted(data[actor_name]["positions"].keys())]

        if clicked_marker == actor_name and (delta_t in data[actor_name]["positions"].keys() or len(data[actor_name]["positions"]) == 1) :
            delete_actor_disabled = False

        if actor_type == "actor":
            mapch.append(
                dl.DivMarker(
                    id={"role": "actor-marker", "name": actor_name},
                    position=get_position_at(delta_t, data[actor_name]["positions"], default_positions.get(actor_name)),
                    iconOptions=dict(
                        id=f"actor-marker-icon-{actor_name}",
                        html=f"<div id=\"actor-marker-div-{actor_name}\" style=\"background-color: {actor_color}{transperancy};\">{actor_name}</div>",
                        className='marker-standard',
                        iconSize=[30, 30],
                        iconAnchor=[20,20]
                    ), 
                    draggable=True,
                    eventHandlers=markerEventHandlers,
                    interactive=True
                )
            )


            for point in actor_path:
                mapch.append(
                    dl.CircleMarker(
                        id={"role": "actor-trajectory-point", "name": f"{actor_name}_{point[0]}_{point[1]}"},
                        center=point, 
                        radius=5, 
                        color=actor_color,
                        eventHandlers=pointEventHandlers,
                        interactive=True
                    )
                )

        
            mapch.append(
                dl.Polyline(
                    id=f"actor-trajectory-{actor_name}", 
                    positions=actor_path,
                    color=actor_color
                )
            )

        if actor_type == "event":

            event_path = data[actor_name].get("positions")
            if len(event_path) > 0:
                event_time, event_pos = next(iter(event_path.items()))
            else:
                event_pos = center_pos
                event_time = 0

            audio_component = None
            print(mute)

            audio_pos = delta_t - event_time
            play_audio = audio_pos >= 0 # && < duration
            print('marker-pulsating' if play_audio else 'marker-standard')

            if mute != "Tyst" and play_audio:
                audio_component = dash_player.DashPlayer(
                            id={"role": "event-audio-player", "name": actor_name},
                            url="https://wpu.nu/images/3/39/01-Samtal-LL-LAC-original.flac",
                            controls=False,
                            #width="100%",
                            #height="250px",
                            playing=True,
                            seekTo=audio_pos,
                            intervalCurrentTime=1000
                        )
                

            mapch.append(
                dl.DivMarker(
                    id={"role": "actor-marker", "name": actor_name},
                    position=event_pos,
                    iconOptions=dict(
                        id=f"actor-marker-icon-{actor_name}",
                        html=f"<div id=\"actor-marker-div-{actor_name}\" style=\"background-color: {actor_color}{transperancy};\">{actor_name}</div>",
                        className='marker-pulsating' if play_audio else 'marker-standard',
                        iconSize=[30, 30],
                        iconAnchor=[20,20]
                    ), 
                    draggable=True,
                    eventHandlers=markerEventHandlers,
                    interactive=True,
                    children=audio_component
                )
            )



        idx += 1

    if time_zoom[0] > delta_t:
        time_zoom[0] = delta_t
    if time_zoom[1] < delta_t:
        time_zoom[1] = delta_t

    
    return [mapch, t, t.date(), time_zoom, delete_actor_disabled]




@app.callback(
        Output("time-point-slider", "min"), 
        Output("time-point-slider", "max"), 
        Input("time-zoom-slider", "value"))
def update_slider_range(values):
    return values

@app.callback(
    Output({'role': 'event-audio-player', "name": MATCH}, 'playing'),
    Output({'role': 'event-audio-player', "name": MATCH}, 'seekTo'),
    Input({"role":  'event-audio-player', "name": MATCH}, 'id'),
    Input({"role":  'event-audio-player', "name": MATCH}, 'duration'),
    Input({"role":  'event-audio-player', "name": MATCH}, 'currentTime'),
    Input("time-point-slider", "value"),
    State("local-store", "data"))
def stop_audio_segment(actor_data, audio_duration, audio_current_time, delta_t, data):
    print("stop_audio_segment")
    

    if delta_t is None or audio_current_time is None:
        raise PreventUpdate

    if not data:
        raise PreventUpdate

    #pprint(actor_data)
    #actor = json.loads(actor_data)
    actor_name = actor_data["name"]
    print(actor_name)


    data[actor_name]["positions"] = {int(k):v for k,v in data[actor_name]["positions"].items()}

    
    event_time = next(iter(data[actor_name]["positions"].keys()))
    
    print(event_time)
    if event_time + audio_duration < delta_t:
        return [False, 0]

    if event_time > delta_t:
        return [False, 0]

    should_start_at = delta_t - event_time
    should_stop_at = should_start_at + 1

    if should_start_at <= audio_current_time <= should_stop_at:
        return [True, None]

    if audio_current_time > should_stop_at:
        return [False, 0]

    if audio_current_time < should_start_at:
        return [True, should_start_at]

    


    return [False, 0]


@app.callback(
        Output("local-store", "data"), 
        Input("save-positions-btn", 'n_clicks'),
        Input("new-actor-save-btn", 'n_clicks'),
        Input("new-event-save-btn", 'n_clicks'),   
        Input("delete-actor-btn", 'n_clicks'),                
        State("time-point-slider", "value"),
        State({'role': 'actor-marker', "name": ALL}, 'moveend'),
        State({'role': 'actor-marker', "name": ALL}, 'actor'),
        State("new-actor-name-input", "value"),
        State("new-actor-modal-color", "value"),
        State("new-event-name-input", "value"),
        State("new-event-modal-color", "value"),
        State("clicked-marker", "children"),       
        State("local-store", "data"))
def save_positions_at_timestamp(n_clicks_save_pos, n_clicks_save_new_actor, n_clicks_save_new_event, n_clicks_delete_actor, delta_t, moveend, moveactor, new_actor_name, new_actor_color, new_event_name, new_event_color, clicked_marker, data):

    global actors
    print("save_positions_at_timestamp")

    triggered = ctx.triggered


    if len(triggered) > 1 or (len(triggered) == 1 and triggered[0]['value'] == 0):
        raise PreventUpdate
    
    if delta_t is None:
        raise PreventUpdate

    
    if ctx.triggered_id == "new-actor-save-btn":
        data[new_actor_name] = {
                "positions": {delta_t:center_pos},
                "color": new_actor_color,
                "type": "actor"
            }
        return data

    if ctx.triggered_id == "new-event-save-btn":
        data[new_event_name] = {
                "positions": {delta_t:center_pos},
                "color": new_event_color,
                "type": "event",
                "sound": "../assets/LAC-samtal_1.mp3",
                "sound_offset": 0.34
            }
        return data

    
    if not data:
        data = actors
    else:
        for actor in data.keys():
            data[actor]["positions"] = {int(k):v for k,v in data[actor]["positions"].items()}


    if ctx.triggered_id == "delete-actor-btn" and len(clicked_marker) > 0:
        if clicked_marker in data.keys():
            if len(data[clicked_marker]["positions"]) == 1:
                del data[clicked_marker]
            elif delta_t in data[clicked_marker]["positions"].keys():
                del data[clicked_marker]["positions"][delta_t]

    
    for actor, position in zip(moveactor, moveend):
        if actor is None or position is None:
            continue
        
        actor_data = json.loads(actor)
        data[actor_data["name"]]["positions"][delta_t] = position
        

    #pprint(data)

    return data





if __name__ == '__main__':
    app.run_server(
        #host='10.0.0.40',
        #threaded=True,
        host="0.0.0.0",
        port='80',
        #debug=True
        )

