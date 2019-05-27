# -*- coding: utf-8 -*-
from mpl_toolkits.basemap import Basemap
import osr
import gdal
import numpy as np
from sys import argv
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
import datetime
import os

# Create export directory if it doesn't exist yet
export_dir = os.getcwd() + "\\export\\"
if not os.path.exists(export_dir):
    os.mkdir(export_dir)

# Version
VERS_MAJ = 2
VERS_MIN = 0

print("\033[93mGeoTIFF to map v" + str(VERS_MAJ) + "." + str(VERS_MIN) + "\033[0m\n")

str_usage = "Usage: geotiff_to_map.py [GeoTIFF] [Excel] [Gamma_correction{0|1}] [Temperature_gamma] [Brightness_gamma]\n"

# Return the number of console arguments in a variable
argn = len(argv)

# Default values
arg_geotiff = None
arg_excel = None
arg_gamcorr = 0
arg_gamcorrTI = 1
arg_gamcorrBI = 0.5

# Check number of arguments passed
if argn == 3:
    arg_geotiff = argv[1]
    arg_excel = argv[2]
elif argn == 4:
    arg_gamcorr = int(argv[3])
    if arg_gamcorr:
        print("Using default values for gamma correction: TI = " + str(arg_gamcorrTI) + " BI = " + str(arg_gamcorrBI) + "\n")
    arg_geotiff = argv[1]
    arg_excel = argv[2]
elif argn == 6:
    arg_gamcorr = int(argv[3])
    if arg_gamcorr:
        arg_gamcorrTI = float(argv[4])
        arg_gamcorrBI = float(argv[5])
    arg_geotiff = argv[1]
    arg_excel = argv[2]
else:
    print(str_usage)
    exit(-1)

time_now = datetime.datetime.now()
str_time_clean = time_now.strftime('%Y-%m-%d %H:%M:%S')
str_time_short = time_now.strftime('%Y%m%d%H%M%S')

# Read GeoTIFF data into a GDAL object (dataset)
geo_dataset = gdal.Open(arg_geotiff)

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
      "Distance for longtitude (x) is " + str(x_resolution * 111319.49) + "*cos(latitude) [meters/pixel].\n"
      "Distance for latitude (y) is " + str(-1*y_resolution * 110946.25) + " [meters/pixel].\n")

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

# Get each channel seperately
data4 = data[0, :, :].T     # *-1 removes land and low clouds (unless low gamma (<1) and high reflectance)
data9 = data[1, :, :].T     #
data10 = data[2, :, :].T    #

## For debugging purposes
# data4 = np.zeros(np.shape(data4))
# data9 = np.zeros(np.shape(data4))
# data10 = np.zeros(np.shape(data4))

# Gamma correction is disabled by default
if arg_gamcorr:
    # Gamma correction for IR channels
    T_min = np.min(data9)
    T_max = np.max(data9)
    T_med = (T_max-T_min)/2
    data9 = np.where(data9 < T_med, 128 - 128*((T_med-data9)/float(T_med-T_min))**(1/(float(arg_gamcorrTI)**2)), 128 + 128*((T_med-data9)/float(T_med-T_min))**(1/(float(arg_gamcorrTI))))

    T_min = np.min(data10)
    T_max = np.max(data10)
    T_med = (T_max-T_min)/2
    data10 = np.where(data10 < T_med, 128 - 128*((T_med-data10)/float(T_med-T_min))**(1/(float(arg_gamcorrTI)**2)), 128 + 128*((T_med-data10)/float(T_med-T_min))**(1/(float(arg_gamcorrTI))))

    # Gamma correction for VIS channels
    BTmin = np.min(data4)
    BTmax = np.max(data4)
    data4 = 255*((data4-BTmin)/float(BTmax-BTmin))**(1/float(arg_gamcorrBI))

# Normalize
data4 = data4/float(255)
data9 = data9/float(255)
data10 = data10/float(255)

# Combine channels
data_new = (data4 - (data9 + data10))*255

# Shift values to 0-255
difference_minmax = np.abs(np.min(data_new)) + np.abs(np.max(data_new))
data_new = ((data_new - np.min(data_new))/difference_minmax)*255

data = data_new

# Plot data at coordinates converted_x and converted_y using a color map
bm.pcolormesh(x_coords, y_coords, data, cmap=plt.cm.gray)

# Draw coastlines on map
bm.drawcoastlines(linewidth=1, color='cyan')

# Reading excel from file and select sheet
df = pd.read_excel(arg_excel, sheet_name='Sheet1')

# Retrieve dataframe columns latitude and lontitude
listLat = df['latitude']
listLon = df['longitude']

# Using basemap instance to convert lontitude and lattitude to position on the map
xlon, ylat = bm(listLon.tolist(), listLat.tolist())

# Plot the route as lines on the map
plt.plot(xlon, ylat, zorder=10, linewidth=0.5, alpha=1, color='magenta')

# TODO: see gps_read.py file
xlon_me = 26.22
ylat_me = 12.072

# Using basemap instance to convert lontitude and lattitude to position on the map
xlon_me_map, ylat_me_map = bm(xlon_me, ylat_me)

# Plot the current location as a cross on the map
plt.plot(xlon_me_map, ylat_me_map, zorder=200, marker='+', alpha=1, markersize=4, color='yellow')

# Enable drawing title and legend
enable_titlelegend = 1

if enable_titlelegend:
    # Draw title and legend on figure
    title_x, title_y = bm(xmin+(xmax-xmin)/2, ymax-2)
    title_str = 'MSG1 ' + str_time_clean
    fontsize_title = 40
    bbox_title = dict(boxstyle='round,pad=0.1', fc='black', edgecolor='none', alpha=0.5)
    plt.annotate(title_str, xy=(title_x, title_y), fontsize=fontsize_title, color='white', ha='center', bbox=bbox_title)
    bbox_legend = dict(boxstyle='round,pad=0.1', fc='white', edgecolor='none', alpha=0.3)
    fontsize_legend = 30
    rte_legend_x, rte_legend_y = bm(xmin+0.5, ymax-2)
    plt.annotate('Route', xy=(rte_legend_x, rte_legend_y), fontsize=fontsize_legend, color='magenta', bbox=bbox_legend)
    you_legend_x, you_legend_y = bm(xmin+0.5, ymax-4)
    plt.annotate('Current location', xy=(you_legend_x, you_legend_y), fontsize=fontsize_legend, color='yellow', bbox=bbox_legend)

# Turn axis off (remove border)
plt.axis('off')

# Saving an image from the generated map and close the figure
str_gammacorrection = '_GCOR' if arg_gamcorr else ''
str_finalimage = export_dir + "MSG1_" + str_time_short + str_gammacorrection + ".png"
plt.savefig(str_finalimage, dpi=72, bbox_inches='tight', pad_inches=0)
plt.close()

print("Final image saved as " + str_finalimage + ".\n")

im = Image.open(str_finalimage)
im_width = im.size[0]
im_height = im.size[1]

dist_lat = -1*y_resolution * 110946.25 * (px_y/float(im_height))
dist_lng = x_resolution * 111319.49 * (px_x/float(im_width))

print("The final image has following properties: \n"
      "Distance for longtitude (x) is " + str(dist_lng) + "*cos(latitude) [meters/pixel].\n"
      "Distance for latitude (y) is " + str(dist_lat) + " [meters/pixel].\n")

im.close()

