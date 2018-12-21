import numpy as np
import matplotlib.pyplot as plt
import pickle
import scipy.stats

from bokeh.core.properties import Instance, String
from bokeh.models import ColumnDataSource, LayoutDOM, Spacer, HoverTool, Span
from bokeh.io import show

from bokeh.io import curdoc
from bokeh.layouts import row, column, layout, widgetbox
from bokeh.models.widgets import PreText, Select, Slider, TextInput, Button
from bokeh.plotting import figure, output_file, save

open_path = '/Users/miksch/Thesis_Files/Processed/landsat/EL_LS8/'
fig_path = ''

raster_bands = pickle.load(open(open_path+'raster_bands.p','rb'))
raster_info = pickle.load(open(open_path+'raster_info.p','rb'))

ndvi_band='NDVI'
tir_band='B10'

#Read in list of landsat aquisitions
band_list = list(raster_bands.keys())
ls_ret = Select(title='Overpass Time:',value=band_list[0],options=band_list) 

#Initialize other widgets and source
ndvio = TextInput(title='NDVIo', value=str(raster_info[band_list[0]]['ndvio']))
ndvis = TextInput(title='NDVIs', value=str(raster_info[band_list[0]]['ndvis']))
tir_max = TextInput(title='Tmax', value=str(raster_info[band_list[0]]['tir_max']))
tir_min = TextInput(title='Tmin', value=str(raster_info[band_list[0]]['tir_min']))

warm_t1 = TextInput(title='Warm T1', value=str(raster_info[band_list[0]]['we_points'][0,0]))
warm_t2 = TextInput(title='Warm T2', value=str(raster_info[band_list[0]]['we_points'][0,1]))
warm_n1 = TextInput(title='Warm N1', value=str(raster_info[band_list[0]]['we_points'][1,0]))
warm_n2 = TextInput(title='Warm N2', value=str(raster_info[band_list[0]]['we_points'][1,1]))

save_button = Button(label='Save All', button_type='default')

src = ColumnDataSource(data=dict(tir=[], ndvi=[], tstar=[], fr=[], ef=[]))
we_src = ColumnDataSource(data=dict(we=[],tirs=[]))

#Based on https://ideone.com/ItifKv
#Converts string output from TextInput to float, returns 0 if it can't
def convert_to_float(frac_str):   
    try:
        return float(frac_str)
    except ValueError:
        try:
            num, denom = frac_str.split('/')
        except:
            return np.nan
    try:
        leading, num = num.split(' ')
        whole = float(leading)
    except ValueError:
        whole = 0

    frac = float(num) / float(denom)
    return whole - frac if whole < 0 else whole + frac

hover = HoverTool(tooltips=[
    ("(x,y)", "($x, $y)"),
])

#Plot 1: Raw triangle (semi-large to select points)
p1 = figure(title='Raw Triangle',tools=['pan',hover,'wheel_zoom','crosshair'],x_range=[270.,325.],y_range=[0.,1.],lod_threshold=1000,output_backend='webgl')
p1.xaxis.axis_label = 'Tir'
p1.yaxis.axis_label = 'NDVI'
p1.scatter(x='tir',y='ndvi',source=src,line_alpha=.2,fill_alpha=.2)
    
ndvis_line = Span(location=convert_to_float(ndvis.value),dimension='width',line_color='SlateGrey',line_width=3,line_dash='dashed')
ndvio_line = Span(location=convert_to_float(ndvio.value),dimension='width',line_color='SlateGrey',line_width=3,line_dash='dashed')
tir_max_line = Span(location=convert_to_float(tir_max.value),dimension='height',line_color='SlateGrey',line_width=3,line_dash='dashed')
tir_min_line = Span(location=convert_to_float(tir_min.value),dimension='height',line_color='SlateGrey',line_width=3,line_dash='dashed')
p1.renderers.extend([ndvis_line,ndvio_line,tir_max_line,tir_min_line])

#Plot 2: Fixed triangle
p2 = figure(title='Scaled Triangle',tools=['pan',hover,'wheel_zoom','crosshair'],x_range=[0.,1.],y_range=[0.,1.],lod_threshold=1000,output_backend='webgl')
p2.xaxis.axis_label = 'Tstar'
p2.yaxis.axis_label = 'Fr'
p2.scatter(x='tstar',y='fr',source=src,color='purple',line_alpha=.2,fill_alpha=.2)
p2.line(x='tirs', y='we',color='red',source=we_src,line_width=3)

#Get the temperatures, warm edge line, and slope/intercept values for the warm edge 
#Based on two points
def warm_edge(points,num_range=None):   
    m,b = scipy.stats.linregress(points)[0:2]    
    ts = np.linspace(num_range[0],num_range[1],100)
    return ts, m*ts + b,m,b

#Calculate evaporative fraction for normalized triangle 
#Based on slope/intercept of warm edge
def evap_fraction(tstars,frs,m,b):
    x_vals = (frs-b) / m
    ef_soil = 1 - tstars/x_vals
    return ef_soil*(1-frs)+1.*frs

#Normalize tir/NDVI space based on user input
def normalize_triangle(tir,ndvi,tmin,tmax,ndvis,ndvio):
    t_star = (tir-tmin) / (tmax-tmin)
    Fr = ((ndvi-ndvio)/(ndvis-ndvio)) ** 2
    return t_star, Fr

#Callback for when the text inputs are changed
def update_all(attrname,old,new):
    ls_date = ls_ret.value
    nd_o = convert_to_float(ndvio.value)
    nd_s = convert_to_float(ndvis.value)
    t_max = convert_to_float(tir_max.value)
    t_min = convert_to_float(tir_min.value)
    
    tir_i = raster_bands[ls_date][tir_band]
    ndvi_i = raster_bands[ls_date][ndvi_band]
    tstar,fr = normalize_triangle(tir_i,ndvi_i,t_min,t_max,nd_s,nd_o) 
    
    we_points = np.array(([convert_to_float(warm_t1.value),convert_to_float(warm_t2.value)],
                          [convert_to_float(warm_n1.value),convert_to_float(warm_n2.value)]))
    tirs,we_line,m,b = warm_edge(we_points,we_points[0,:])
    
    ef = evap_fraction(tstar,fr,m,b)
    
    src.data = dict(tir=tir_i, ndvi=ndvi_i, tstar=tstar, fr=fr, ef=ef)
    we_src.data = dict(we=we_line,tirs=tirs)
    ndvis_line.location=convert_to_float(ndvis.value)
    ndvio_line.location=convert_to_float(ndvio.value)
    tir_max_line.location=convert_to_float(tir_max.value)
    tir_min_line.location=convert_to_float(tir_min.value)
   

#Callback for when the date is changed
def update_date(attrname,old,new):
    ls_date = ls_ret.value
    
    ndvio.value = str(raster_info[ls_date]['ndvio'])
    ndvis.value = str(raster_info[ls_date]['ndvis'])
    tir_max.value = str(raster_info[ls_date]['tir_max'])
    tir_min.value = str(raster_info[ls_date]['tir_min'])

    warm_t1.value = str(raster_info[ls_date]['we_points'][0,0])
    warm_t2.value = str(raster_info[ls_date]['we_points'][0,1])
    warm_n1.value = str(raster_info[ls_date]['we_points'][1,0])
    warm_n2.value = str(raster_info[ls_date]['we_points'][1,1])

    nd_o = convert_to_float(ndvio.value)
    nd_s = convert_to_float(ndvis.value)
    t_max = convert_to_float(tir_max.value)
    t_min = convert_to_float(tir_min.value)
    
    tir_i = raster_bands[ls_date][tir_band]
    ndvi_i = raster_bands[ls_date][ndvi_band]
    tstar,fr = normalize_triangle(tir_i,ndvi_i,t_min,t_max,nd_s,nd_o) 
    
    we_points = np.array(([convert_to_float(warm_t1.value),convert_to_float(warm_t2.value)],
                          [convert_to_float(warm_n1.value),convert_to_float(warm_n2.value)]))
    tirs,we_line,m,b = warm_edge(we_points,we_points[0,:])
    
    ef = evap_fraction(tstar,fr,m,b)
    
    
    
    src.data = dict(tir=tir_i, ndvi=ndvi_i, tstar=tstar, fr=fr, ef=ef)
    we_src.data = dict(we=we_line,tirs=tirs)
    ndvis_line.location=convert_to_float(ndvis.value)
    ndvio_line.location=convert_to_float(ndvio.value)
    tir_max_line.location=convert_to_float(tir_max.value)
    tir_min_line.location=convert_to_float(tir_min.value)   

#Button to pickle all of the inputs
def save_all():
    for label,var in zip(['ndvio','ndvis','tir_max','tir_min'],[ndvio,ndvis,tir_max,tir_min]):
        raster_info[ls_ret.value][label] = convert_to_float(var.value)
        
    
    raster_info[ls_ret.value]['we_points'] = np.array(([convert_to_float(warm_t1.value),convert_to_float(warm_t2.value)],
                                                       [convert_to_float(warm_n1.value),convert_to_float(warm_n2.value)]))
    
    print(raster_info[ls_ret.value]['we_points'])
    raster_bands[ls_ret.value]['EF'] = src.data['ef']
    raster_bands[ls_ret.value]['FR'] = src.data['fr']
    raster_bands[ls_ret.value]['tstar'] = src.data['tstar']
    
    pickle.dump(raster_bands,open(open_path+'raster_bands.p','wb'))    
    pickle.dump(raster_info,open(open_path+'raster_info.p','wb'))
    
#Layout
inits = widgetbox(ls_ret,ndvio,ndvis,tir_min,tir_max,warm_t1,warm_n1,warm_t2,warm_n2,save_button)

layout = row(inits,p1,p2)

#Link callbacks to widgets
ls_ret.on_change('value',update_date)

for w in [ndvio,ndvis,tir_max,tir_min,warm_t1,warm_n1,warm_t2,warm_n2]:
    w.on_change('value',update_all)

save_button.on_click(save_all)

#Update document
curdoc().add_root(layout)
curdoc().title = 'Triangle Method'
