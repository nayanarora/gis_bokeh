
import requests
import json
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import HoverTool,LabelSet,ColumnDataSource
from bokeh.tile_providers import get_provider, STAMEN_TERRAIN
import numpy as np
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler

#FUNCTION TO CONVERT GCS WGS84 TO WEB MERCATOR
#DATAFRAME
def wgs84_to_web_mercator(df, lon="long", lat="lat"):
    k = 6378137
    df["x"] = df[lon] * (k * np.pi/180.0)
    df["y"] = np.log(np.tan((90 + df[lat]) * np.pi/360.0)) * k
    return df

#POINT
def wgs84_web_mercator_point(lon,lat):
    k = 6378137
    x= lon * (k * np.pi/180.0)
    y= np.log(np.tan((90 + lat) * np.pi/360.0)) * k
    return x,y

#AREA EXTENT COORDINATE WGS84
lon_min,lat_min=-125.974,30.038
lon_max,lat_max=-68.748,52.214

#COORDINATE CONVERSION
xy_min=wgs84_web_mercator_point(lon_min,lat_min)
xy_max=wgs84_web_mercator_point(lon_max,lat_max)

#COORDINATE RANGE IN WEB MERCATOR
x_range,y_range=([xy_min[0],xy_max[0]], [xy_min[1],xy_max[1]])

#REST API QUERY
user_name='jaswin90'
password='jaswin90'
url_data='https://'+user_name+':'+password+'@opensky-network.org/api/states/all?'+'lamin='+str(lat_min)+'&lomin='+str(lon_min)+'&lamax='+str(lat_max)+'&lomax='+str(lon_max)

    
#FLIGHT TRACKING FUNCTION
def flight_tracking(doc):
    # init bokeh column data source
    flight_source = ColumnDataSource({
        'icao24':[],'callsign':[],'origin_country':[],
        'time_position':[],'last_contact':[],'long':[],'lat':[],
        'baro_altitude':[],'on_ground':[],'velocity':[],'true_track':[],
        'vertical_rate':[],'sensors':[],'geo_altitude':[],'squawk':[],'spi':[],'position_source':[],'x':[],'y':[],
        'rot_angle':[],'url':[]
    })
    
    # UPDATING FLIGHT DATA
    def update():
        response=requests.get(url_data).json()
        
        #CONVERT TO PANDAS DATAFRAME
        col_name=['icao24','callsign','origin_country','time_position','last_contact','long','lat','baro_altitude','on_ground','velocity',       
'true_track','vertical_rate','sensors','geo_altitude','squawk','spi','position_source']
       
        flight_df=pd.DataFrame(response['states']) 
        flight_df=flight_df.loc[0:2,0:16] 
        flight_df.columns=col_name
        wgs84_to_web_mercator(flight_df)
        flight_df=flight_df.fillna('No Data')
        flight_df['rot_angle']=flight_df['true_track']*-1
        icon_url='data:image/png;base64,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' #icon url
        flight_df['url']=icon_url
        
        # CONVERT TO BOKEH DATASOURCE AND STREAMING
        n_roll=len(flight_df.index)
        flight_source.stream(flight_df.to_dict(orient='list'),n_roll)
        
    #CALLBACK UPATE IN AN INTERVAL
    doc.add_periodic_callback(update, 5000) #5000 ms/10000 ms for registered user .    
    #PLOT AIRCRAFT POSITION
    p=figure(x_range=x_range,y_range=y_range,x_axis_type='mercator',y_axis_type='mercator',sizing_mode='scale_width', height=300)
    tile_prov=get_provider(STAMEN_TERRAIN)
    p.add_tile(tile_prov,level='image')
    p.image_url(url='url', x='x', y='y',source=flight_source,anchor='center',angle_units='deg',angle='rot_angle',h_units='screen',w_units='screen',w=40,h=40)
    p.circle('x','y',source=flight_source,fill_color='red',hover_color='yellow',size=10,fill_alpha=0.8,line_width=0)

    #ADD HOVER TOOL AND LABEL
    my_hover=HoverTool()
    my_hover.tooltips=[('Call sign','@callsign'),('Origin Country','@origin_country'),('velocity(m/s)','@velocity'),('Altitude(m)','@baro_altitude')]
    labels = LabelSet(x='x', y='y', text='callsign', level='glyph',
            x_offset=5, y_offset=5, source=flight_source,background_fill_color='white',text_font_size="2pt")
    p.add_tools(my_hover)
    p.add_layout(labels)
    
    doc.title='REAL TIME FLIGHT TRACKING'
    doc.add_root(p)
    
# SERVER CODE
apps = {'/': Application(FunctionHandler(flight_tracking))}
server = Server(apps, port=8078 ) #define an unused port
server.start()
 