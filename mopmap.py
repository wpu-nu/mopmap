
import flask
import json
from datetime import datetime, timedelta, date
from pathlib import Path
from pprint import pprint 

from dash import Dash, ctx, dcc, html, Patch, dash
import dash_leaflet as dl
import dash_mantine_components as dmc
#import dash_player

from dash.dependencies import Input, Output, State, ALL, MATCH
from dash.exceptions import PreventUpdate
from dash_extensions.javascript import assign
from dash_iconify import DashIconify
import urllib
import base64
from dash._utils import AttributeDict


def bp():
  from pudb import set_trace; set_trace()


t0 = datetime(1986, 2, 28, 23, 21, 20)

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

default_state = {
  "selected_actor": None,
  "selected_trajectory_point": None,
  "current_delta_t": 0,
  "actors": {
    "OP": {
      "color": "#FF1111",
      "positions": {
         0: [59.33662248750816, 18.06278754091279],
        30: [59.33622248750816, 18.06178754091279],
      }
    },
    "SE": { 
      "color": "#1133FF",
      "positions": {
        0: [59.33612248750816, 18.062723454091279],
      }
    }
  },
  "events": {
    "MOP": {
      "color": "#FF33FF",
      "position": [59.32662248750816, 18.16278754091279],
      "begin": 0,
      "end": 10
    }
  },
  "positions":{
    "IB": {
      "color": "#FF3300",
      "position": [59.32662248750816, 18.16278754091279]
    }
  }
}

app = Dash(__name__)


def get_position_at(delta_t, positions, default_position=False):
  
  #print(f"delta_t: >{delta_t}<")
  #print(f"positions: >{positions}<")


  if len(positions) == 0:
    return center_pos

  if len(positions) == 1:
    return list(positions.values())[0]

  delta_t = int(delta_t)

  if delta_t in positions.keys():
    return positions[delta_t]

  if delta_t < min(positions.keys()):
    if default_position:
      return default_position
    return positions[min(positions.keys())]

  if delta_t >= max(positions.keys()):
    if default_position:
      return default_position
    return positions[max(positions.keys())]


  ls = min(positions.keys())
  for dt0 in sorted(positions.keys()):
    if dt0 < delta_t:
      ls = dt0
      continue
    break

  le = sorted(positions.keys())[1]
  for dt0 in sorted(positions.keys()):
    if dt0 < delta_t:
      continue
    le = dt0
    break

  #print(ls, le)

  fraction = (delta_t - ls) / (le - ls)

  #print(fraction)

  ps = positions[ls]
  pe = positions[le]


  return [ps[0] + fraction * (pe[0] - ps[0]), ps[1] + fraction * (pe[1] - ps[1])]

markerEventHandlers = dict(
  move=assign("function(e, ctx){ctx.setProps({actor_id: e.target.options.id, move_end_pos: [e.latlng.lat, e.latlng.lng]})}")
)
pointEventHandlers = dict(    
  click=assign("function(e, ctx){console.log(e.target.options.id); ctx.setProps({point_id: e.target.options.id, n_clicks: (ctx.n_clicks == undefined ? 1 : ctx.n_clicks + 1)})}")
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
          children=[
            dl.TileLayer(
              id="tile-layer", 
              #url="http://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}", # Google map with POIs
              url="http://www.google.se/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}",
              #url="http://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}", # Google satelite - no poi
              #url="http://tile.openstreetmap.org/{z}/{x}/{y}.png", # OSM - standard leaflet
              #url="http://tile.opencyclemap.org/cycle/{z}/{x}/{y}.png", # Cycling map, less detailed, API key required
              
              #url="http://maptile.maps.svc.ovi.com/maptiler/maptile/newest/satellite.day/{z}/{x}/{y}/256/png8",
              #url="http://mapproxy.openstreetmap.se/tms/1.0.0/ek_EPSG3857/{z}/{x}/{y}.png",
              #url="http://otile1.mqcdn.com/tiles/1.0.0/osm/{z}/{x}/{y}.png",


              #url="https://api.mapbox.com/styles/v1/wpunu/cllqr1y8x008l01qxeiztc69d/tiles/512/{z}/{x}/{y}?access_token=pk.eyJ1Ijoid3B1bnUiLCJhIjoiY2t3a2ZndGtsMXJtZDJvcG1rY3JpMTBjbCJ9.44r4Yxc_0jFRVz8HBRit2g", # MAPBOX style
              maxNativeZoom=25, 
              maxZoom=25, 
              minZoom=5
            )
          ],
          id="dl-widget", 
          attributionControl=False,
          style={'height': '90vh'}, 
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
          value=t0,
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
    

    html.Div(hidden=True,children=[
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
          inputFormat="YYYY-MM-DD",
        ),
        dmc.ActionIcon(
          DashIconify(icon="bi:caret-right", width=20),
          size="lg",
          variant="outline",
          id="step-forward-d",
        ),
      ])
    )
    ]),
    
    html.Div(hidden=True,children=[
    #dmc.Space(h='lg'),
    #dmc.Divider(label="Tidslinje", labelPosition="center", variant="dashed", ml=35, mr=35),
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
    #dmc.Space(h='xl'),
    #dmc.Space(h='xl'),
    #dmc.Divider(label="Zoom", labelPosition="center", variant="dashed", ml=35, mr=35),
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
    #dmc.Space(h='xl'),
    #dmc.Divider(label="Zoom", labelPosition="center", variant="dashed"),
    #dmc.Space(h='lg'),
    ]),
    dmc.Space(h='md'),
    dmc.Center(children=[
      dmc.Group(children=[
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
          variant="default",
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
        # dmc.Button(
        #     children=["Tyst"],
        #     id='toggle-mute',
        #     variant="outline",
        #     size="xs",
        #     rightIcon=DashIconify(icon="bi:volume-up", width=20),
        # ),
                html.A(id='download-export', download="mopmap.json", href="", target="_blank", hidden=False,
                  children=[
                    dmc.Button(
                      "Spara", 
                      id="export-button",
                      leftIcon=DashIconify(icon="bi:cloud-download", width=20),
                      size="xs",
                      variant="outline",
                      )


                  ]
                ),
                dcc.Upload(
                  id='upload-data',
                  children=[
                    dmc.Button(
                      "Ladda upp", 
                      id="load-data-button",
                      leftIcon=DashIconify(icon="bi:cloud-upload", width=20),
                      size="xs",
                      variant="outline",
                      )
                  ]
                ),

                # dmc.Button(
                #   "Radera positioner",
                #   leftIcon=DashIconify(icon="bi:chevron-bar-right", width=20),
                #   size="xs",
                #   variant="outline",
                #   id="delete-local-storage-button",
                # ),

        ]
      )
    ]),
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
          # dmc.Space(h=20),
          # dmc.Text("Max hastighet"),
          # dmc.ColorPicker(
          #    id="new-actor-modal-color",
          #    value="#880000",
          #    format="hex"
          # ),
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
            placeholder="MOP",
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
    )
])





############ M O D A L S 

@app.callback(
  Output("new-actor-modal", "opened"),
  Input("new-actor-modal-open-btn", "n_clicks"),
  Input("new-actor-modal-close", "n_clicks"),
  Input("new-actor-save-btn", 'n_clicks'))
def open_new_actor_modal(n_clicks_open, n_clicks_close, n_clicks_save):

  if ctx.triggered_id is None:
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

  if ctx.triggered_id is None:
    raise PreventUpdate
  
  if ctx.triggered_id == 'new-event-modal-close':
    return False

  if ctx.triggered_id == 'new-event-save-btn':
    return False

  if ctx.triggered_id == 'new-event-modal-open-btn':
    return True

  return False










################# C H A N G E   O F   M A P   S T A T E 

@app.callback(
  Output("local-store", "data"),
  Output("delete-actor-btn", "disabled"),  
  Output("date-picker", "value"),  
  Output("time-picker", "value"),
  Output("time-point-slider", "value"),
  Input("time-point-slider", "value"),
  Input("time-picker", "value"),
  Input("date-picker", "value"),
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
  Input({'role': 'actor-marker', "name": ALL}, 'n_clicks'),
  Input({'role': 'actor-trajectory-point', "name": ALL}, 'n_clicks'),
  Input("save-positions-btn", 'n_clicks'),
  Input("new-actor-save-btn", 'n_clicks'),
  Input("new-event-save-btn", 'n_clicks'),   
  Input("delete-actor-btn", 'n_clicks'),  
  Input(component_id='upload-data', component_property='contents'),
  Input(component_id='upload-data', component_property='last_modified'),
  State("local-store", "data"),
  State({'role': 'actor-marker', "name": ALL}, 'actor_id'),
  State({'role': 'actor-trajectory-point', "name": ALL}, 'point_id'),
  State({'role': 'actor-marker', "name": ALL}, 'move_end_pos'),
  State("new-actor-name-input", "value"),
  State("new-actor-modal-color", "value"),
  State("new-event-name-input", "value"),
  State("new-event-modal-color", "value")
)
def change_map_state(tp_slider_value, time_picker_value, date_picker_value, fs, fm, fh, fd, sn, bs, bm, bh, bd, sp, 
                                  clicks_actor, clicks_traj_point, clicks_save_positions, 
                                  clicks_save_new_actor, clicks_save_new_event, clicks_delete_actor, 
                                  uploaded_data, upload_timestamp,
                                  data, clicked_actor_id, clicked_traj_point_id, 
                                  moved_actor_pos, 
                                  new_actor_name, new_actor_color, new_event_name, new_event_color):
  

  print("_____")
  print(f"change_map_state trigger: {ctx.triggered_id}")

  if ctx.triggered_id is None:
    raise PreventUpdate

  if data is None or "current_delta_t" not in data:
    data = default_state

  if tp_slider_value is None:
    data["current_delta_t"] = 0

  pprint(ctx.triggered_id)
  print(type(ctx.triggered_id))
  if isinstance(ctx.triggered_id, AttributeDict):
    trigger_dict = ctx.triggered_id
  else:
    try:
      trigger_dict = json.loads(ctx.triggered_id)
    except Exception as e:
      print(e)
      print(type(e))
      trigger_dict = {}

  print("data:")
  pprint(data)
  print("trigger_dict")
  pprint(trigger_dict)
  delete_button_disabled = data.get("selected_actor") is None

  

  if fs is not None and ctx.triggered_id == "step-forward-s":
    data["current_delta_t"] += 1
  elif fm is not None and ctx.triggered_id == "step-forward-m":
    data["current_delta_t"] += 60
  elif fh is not None and ctx.triggered_id == "step-forward-h":
    data["current_delta_t"] += 60 * 60
  elif fd is not None and ctx.triggered_id == "step-forward-d":
    data["current_delta_t"] += 60 * 60 * 24
  elif bs is not None and ctx.triggered_id == "step-back-s":
    data["current_delta_t"] -= 1
  elif bm is not None and ctx.triggered_id == "step-back-m":
    data["current_delta_t"] -= 60
  elif bh is not None and ctx.triggered_id == "step-back-h":
    data["current_delta_t"] -= 60 * 60
  elif bd is not None and ctx.triggered_id == "step-back-d":
    data["current_delta_t"] -= 60 * 60 * 24

  elif sn is not None and ctx.triggered_id == "step-next":
    sorted_actor_positions = sorted([int(i) for i in data[clicked_actor_id]["positions"].keys()], reverse=False)
    if clicked_actor_id in data["actors"]:
      for i in sorted_actor_positions:
        if int(i) > tp_slider_value:
          data["current_delta_t"] = int(i)
          break    

  elif sp is not None and ctx.triggered_id == "step-prev":
    sorted_actor_positions = sorted([int(i) for i in data[clicked_actor_id]["positions"].keys()], reverse=True)
    if clicked_actor_id in data["actors"]:
      for i in sorted_actor_positions:
        if int(i) < tp_slider_value:
          data["current_delta_t"] = int(i)
          break    


  elif any(clicks_actor) and trigger_dict.get("role") == "actor-marker" and trigger_dict.get("name") != data["selected_actor"] :
    data["selected_actor"] = trigger_dict.get("name")
    print(f"Selected actor: {data['selected_actor']}")

  elif ctx.triggered_id == "time-picker" and time_picker_value is not None and date_picker_value is not None:

    x = time_picker_value
    x = date_picker_value.split("T")[0] + "T" + time_picker_value.split("T")[1]
    
    d = datetime.strptime(date_picker_value.split("T")[0] + "T" + time_picker_value.split("T")[1], '%Y-%m-%dT%H:%M:%S') 
    data["current_delta_t"] = (d - t0).total_seconds()
    data["selected_trajectory_point"] = ""
    print(f"new delta_t: {data['current_delta_t']}")


  elif any(clicks_traj_point) and trigger_dict.get("role") == "actor-trajectory-point":
    data["selected_trajectory_point"] = trigger_dict.get("name")
    data["selected_actor"] = trigger_dict.get("name").split("_")[0]
    data["current_delta_t"] = int(trigger_dict.get("name").split("_")[1])
    print(f"Selected trajector point: {data['selected_trajectory_point']}")

  elif ctx.triggered_id == "new-actor-save-btn":
    data["actors"][new_actor_name] = {
        "positions": {data["current_delta_t"]:center_pos},
        "color": new_actor_color,
        "type": "actor"
      }

  elif ctx.triggered_id == "new-event-save-btn":
    data["events"][new_event_name] = {
        "positions": {data["current_delta_t"]:center_pos},
        "color": new_event_color,
        "type": "event",
      }

  elif ctx.triggered_id == "delete-actor-btn" and data["selected_actor"] is not None:
    if data["selected_actor"] in data["actors"].keys():
      if len(data["actors"][data["selected_actor"]]["positions"]) == 1:
        del data["actors"][data["selected_actor"]]
      else:
        pprint(data["actors"][data["selected_actor"]]["positions"])
        del data["actors"][data["selected_actor"]]["positions"][str(data["current_delta_t"])]


  elif ctx.triggered_id == "save-positions-btn":
    for actor, position in zip(clicked_actor_id, moved_actor_pos):
      print(f"{actor=} {position=}")
      if actor is None or position is None:
        continue
      actor_data=json.loads(actor)
      data["actors"][actor_data["name"]]["positions"][data["current_delta_t"]] = position
      data["selected_actor"] = actor_data["name"]
      print("Saving data:")
      pprint(data)
  

  elif ctx.triggered_id == "upload-data":
    print("Loading data from file")
    pprint(uploaded_data)
    actual_data = uploaded_data.split(',')[-1]
    pprint(actual_data)
    local_store_data = json.loads(base64.b64decode(actual_data))
    pprint(local_store_data)
    data = local_store_data
    data["selected_actor"] = ""
    data["selected_trajectory_point"] = ""


  t = t0 + timedelta(seconds=data.get("current_delta_t", 0))
  print("^^^^^")
  return data, delete_button_disabled, t, t, data.get("current_delta_t", 0)










################# D I S P L A Y   M A P

@app.callback(
  Output("dl-widget", "children"),
  Input("local-store", "modified_timestamp"),
  State("local-store", "data"),
  State("dl-widget", "children"),
)
def display_map(mtime, data, map_children):
  
  if data is None or "current_delta_t" not in data:
    data = default_state

  t = t0 + timedelta(seconds=data.get("current_delta_t",0))

  for actor in data["actors"].keys(): # cast delta_t keys to ints
    data["actors"][actor]["positions"] = {int(k):v for k,v in data["actors"][actor]["positions"].items()}
    

  map_children = [map_children[0]]
  delete_actor_disabled = True
  for actor_name, actor_data in data["actors"].items():
    print(f"Drawing actor: {actor_name}")
    
    transperancy = "FF" if data["selected_actor"] == actor_name else "C0"
    print(f"{transperancy=}")
    traj_delta_ts=list(sorted(actor_data["positions"].keys()))
    sorted_actor_path=[actor_data["positions"][p] for p in traj_delta_ts]


    if data["selected_actor"] == actor_name and (data["current_delta_t"] in actor_data["positions"].keys() or len(actor_data["positions"]) == 1):
      delete_actor_disabled = False
    
    map_children.append(
      dl.DivMarker(
        id={"role": "actor-marker", "name": actor_name},
        position=get_position_at(data["current_delta_t"], actor_data["positions"]),
        iconOptions=dict(
          id=f"actor-marker-icon-{actor_name}",
          html=f"<div id=\"actor-marker-div-{actor_name}\" style=\"background-color: {actor_data['color']}{transperancy};\">{actor_name}</div>",
          className='marker-standard',
          iconSize=[30, 30],
          iconAnchor=[20, 20]
        ), 
        draggable=True,
        eventHandlers=markerEventHandlers,
        interactive=True
      )
    )

    for time_point, point in zip(traj_delta_ts, sorted_actor_path):
      map_children.append(
        dl.CircleMarker(
          id={"role": "actor-trajectory-point", "name": f"{actor_name}_{time_point}"},
          center=point, 
          radius=5, 
          color=actor_data["color"],
          eventHandlers=pointEventHandlers,
          interactive=True,
          children=[time_point]
        )
      )

    
    map_children.append(
      dl.Polyline(
         id=f"actor-trajectory-{actor_name}", 
         positions=sorted_actor_path,
         color=actor_data["color"] + transperancy,
       )
    )


    

  # if time_zoom[0] > delta_t:
  #   time_zoom[0] = delta_t
  # if time_zoom[1] < delta_t:
  #   time_zoom[1] = delta_t
  
  
  return map_children




@app.callback(
    Output("time-point-slider", "min"), 
    Output("time-point-slider", "max"), 
    Input("time-zoom-slider", "value"))
def update_slider_range(values):
  return values


@app.callback(
  Output(component_id='download-export', component_property='href'),
  Input('export-button', 'n_clicks'),
  State('local-store', 'data')
)
def export_data(export_button, data):
  if export_button is not None:
    if "selected_actor" in data:
      del data["selected_actor"]
    if "selected_trajectory_point" in data:
      del data["selected_trajectory_point"]
    if "events" in data:
      del data["events"]
    if "positions" in data:
      del data["positions"]
    d = json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False)
    return "data:application/json;charset=utf-8," + urllib.parse.quote(d)



if __name__ == '__main__':
  print("\n"*25)
  app.run_server(
    host="0.0.0.0",
    port='8052',
    debug=True
    )


