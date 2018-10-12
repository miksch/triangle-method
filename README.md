# triangle-method

Scripts, apps, and programs used to calculate evaporative fraciton for remotely sensed data using the Triangle Method (Carlson 2007 and Carlson 2013).

### tri_method_standalone
Bokeh server app written in November/December 2017 to process Landsat 8 images for the Ogden metro. Does not include NLCD filtering for impervious/built surfaces or support for MODIS.
Contents: triangle_method.py, raster_proc.py, raster_process.py

### tri_method_jupyter
Interactive jupyter notebook system that takes images, normalizes NDVI and brightness temperatures, and allows user to put in coordinates to create warm edge.
(future testing for Landsat 8, MODIS, Sentinel, possibly planet?)
