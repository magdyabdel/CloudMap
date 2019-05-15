# -*- coding: utf-8 -*-
from mpl_toolkits.basemap import Basemap
import osr
import gdal
import numpy as np
from sys import argv
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image

VERS_MAJ = 1
VERS_MIN = 0

print("\033[93mGeoTIFF to map v" + str(VERS_MAJ) + "." + str(VERS_MIN) + "\033[0m\n")

# Return the console arguments in a variable
# Usage: filetoread[n]
filetoread = argv

# Read GeoTIFF data into a GDAL object (dataset)
geo_dataset = gdal.Open(filetoread[1])

# Reading GDAL dataset as array to be able to plot it afterwards
data = geo_dataset.ReadAsArray()

# Read in GeoTransform data where (in a north up image without any rotation or shearing):
# GeoTransform[0] = top left x coordinate (longtitude)
# GeoTransform[1] = pixel width (w-e) [degree/pixel]
# GeoTransform[2] = 0
# GeoTransform[3] = top left y coordinate (latitude)
# GeoTransform[4] = 0
# GeoTransform[5] = pixel height (n-s) (negative value) [degree/pixel]
gt = geo_dataset.GetGeoTransform()
# Read projection from GDAL object
proj = geo_dataset.GetProjection()

x_resolution = gt[1]
y_resolution = gt[5]

# RasterXSize and RasterYSize return the raster width and height in pixels
px_x = geo_dataset.RasterXSize
px_y = geo_dataset.RasterYSize

# Return minimum and maximum coordinates of the GeoTIFF image
# Note: Adding or removing half the resolution is a small correction needed to align the data
xmin = gt[0] + x_resolution * 0.5
xmax = gt[0] + (x_resolution * px_x) - x_resolution * 0.5
ymin = gt[3] + (y_resolution * px_y) + y_resolution * 0.5
ymax = gt[3] - y_resolution * 0.5


print("The original image has following properties: \n"
      "Distance for latitude (y) is " + str(-1*y_resolution * 110946.25) + " [meters/pixel].\n"
      "Distance for longtitude (x) is " + str(x_resolution * 111319.49) + "*cos(latitude) [meters/pixel].\n"
      "Note: We multiply by the cosine of latitude because it's dependent.\n")

# Clear dataset
geo_dataset = None

# Create a dense meshgrid from coordindates from the original dataset
original_xy = np.mgrid[xmin:xmax + x_resolution:x_resolution, ymax + y_resolution:ymin:y_resolution]

# Create the figure (figsize is given in inches)
fig = plt.figure(figsize=(2*px_x/96, 2*px_y/96))

# Create the projection objects for the conversion
# Get original projection
origin_proj = osr.SpatialReference()
origin_proj.ImportFromWkt(proj)
origin_proj.AutoIdentifyEPSG()
epsg_code = origin_proj.GetAttrValue("AUTHORITY", 1)

# Create basemap object
# Note: We choose mercator projection and only show map from original GeoTIFF file
bm = Basemap(epsg=epsg_code, llcrnrlat=ymin, urcrnrlat=ymax, llcrnrlon=xmin, urcrnrlon=xmax, resolution='l')

# Return the dimensions of original_xy
dim = original_xy[0, :, :].shape
# Return total number of elements in original_xy
sz = original_xy[0, :, :].size
# Reshape: Reshape the original_xy to an mxn (m=2, n=sz) matrix and transpose it
# Array: Create an array from transformed points with first column x
xy_array = np.array(original_xy.reshape(2, sz).T)
# Reshape the xy_array from a one dimensional matrix to a matrix of mx1 (m=dim) dimensions x_coords and y_coords
x_coords = xy_array[:, 0].reshape(dim)
y_coords = xy_array[:, 1].reshape(dim)

# Plot data at coordinates converted_x and converted_y using a color map
bm.pcolormesh(x_coords, y_coords, data[0, :, :].T, cmap=plt.cm.gray)

# Draw coastlines on map
bm.drawcoastlines(linewidth=1)

# Reading excel from file and select sheet
df = pd.read_excel(filetoread[2], sheet_name='Sheet1')

# Retrieve dataframe columns latitude and lontitude
listLat = df['latitude']
listLon = df['longitude']

# Using basemap instance to convert lontitude and lattitude to position on the map
xlon, ylat = bm(listLon.tolist(), listLat.tolist())

# Plot the route as lines on the map
plt.plot(xlon, ylat, zorder=10, linewidth=0.5, alpha=1, color='Red')

# TODO: see gps_read.py file
xlon_me = 134.1791
ylat_me = -28.36473

# Using basemap instance to convert lontitude and lattitude to position on the map
xlon_me_map, ylat_me_map = bm(xlon_me, ylat_me)

# Plot the current location as a cross on the map
plt.plot(xlon_me_map, ylat_me_map, zorder=200, marker='+', alpha=1, markersize=4, color='Yellow')

# Draw title and legend on figure
title_x, title_y = bm(xmin+(xmax-xmin)/2, ymax-1)
plt.annotate('Australian cloud map', xy=(title_x, title_y), fontsize=60, color='white', ha='center')
bbox_legend = dict(boxstyle='round,pad=0.1', fc='white', edgecolor='none', alpha=0.3)
fontsize_legend = 40
rte_legend_x, rte_legend_y = bm(xmin+0.5, ymax-2)
plt.annotate('Route', xy=(rte_legend_x, rte_legend_y), fontsize=fontsize_legend, color='red', bbox=bbox_legend)
you_legend_x, you_legend_y = bm(xmin+0.5, ymax-3)
plt.annotate('Current location', xy=(you_legend_x, you_legend_y), fontsize=fontsize_legend, color='yellow', bbox=bbox_legend)

# Turn axis off (remove border)
plt.axis('off')

# Saving an image from the generated map and close the figure
plt.savefig('world.png', dpi=72, bbox_inches='tight', pad_inches=0)
plt.close()

im = Image.open('world.png')
im_width = im.size[0]
im_height = im.size[1]

dist_lat = -1*y_resolution * 110946.25 * (im_height/float(px_y))
dist_lng = x_resolution * 111319.49 * (im_width/float(px_x))

print("The final image has following properties: \n"
      "Distance for latitude (y) is " + str(dist_lat) + " [meters/pixel].\n"
      "Distance for longtitude (x) is " + str(dist_lng) + "*cos(latitude) [meters/pixel].\n"
      "Note: We multiply by the cosine of latitude because it's dependent.")

im.close()

