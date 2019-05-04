# -*- coding: utf-8 -*-
from mpl_toolkits.basemap import Basemap
import osr
import gdal
import numpy as np
from sys import argv
import matplotlib.pyplot as plt
import pandas as pd


def convert_xy_projection(source_xy, source_projection, convert_projection):
    """
    Function to convert GeoTIFF file coordinates with origin_proj as projection into convert_projection projection.
    :param source_xy: Original XY coordinates from GeoTIFF file
    :param source_projection: Projection of original XY coordinates from GeoTIFF file
    :param convert_projection: Desired projection to convert original XY coordinates into
    :return: x_out, y_out - Two mxn matrices with converted projection data
    """

    # Return the dimensions of source_xy
    shape = source_xy[0, :, :].shape
    # Return total number of elements in source_xy
    size = source_xy[0, :, :].size

    # Create a CoordinateTransformation object with specified source_projection and convert_projection
    ct = osr.CoordinateTransformation(source_projection, convert_projection)

    # Reshape: Reshape the source_xy to an mxn (bm=2, n=size) matrix and transpose it
    # TransformPoints: Convert the reshaped matrix's coordinates to the desired convert_projection as
    # defined by the ct object
    # Array: Create an array from transformed points with first column x
    xy_target = np.array(ct.TransformPoints(source_xy.reshape(2, size).T))

    # Reshape the xy_target from a one dimensional matrix to a matrix of mxn dimensions x_out and y_out
    x_out = xy_target[:, 0].reshape(shape)
    y_out = xy_target[:, 1].reshape(shape)

    return x_out, y_out


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

# print("X_RES = " + str(x_resolution) + "\nY_RES = " + str(y_resolution))

# Return minimum and maximum coordinates of the GeoTIFF image
# Note: RasterXSize and RasterYSize return the raster width and height in pixels
# Note: Adding or removing half the resolution is a small correction
xmin = gt[0] + x_resolution * 0.5
xmax = gt[0] + (x_resolution * geo_dataset.RasterXSize) - x_resolution * 0.5
ymin = gt[3] + (y_resolution * geo_dataset.RasterYSize) + y_resolution * 0.5
ymax = gt[3] - y_resolution * 0.5

px_x = geo_dataset.RasterXSize
px_y = geo_dataset.RasterYSize

# print("XMIN = " + str(xmin) + "\nXMAX = " + str(xmax))
# print("YMIN = " + str(ymin) + "\nYMAX = " + str(ymax))

# TODO: Fix for final image (this is currently only for original image)
print("Distance for latitude (y) is " + str(-1*y_resolution * 110946.25) + " [meters/pixel].")
print("Distance for longtitude (x) is " + str(x_resolution * 111319.49) + "*cos(latitude) [meters/pixel].")
print("Note: We multiply by the cosine of latitude because it's dependent.")

# Clear dataset
geo_dataset = None

# Create a dense meshgrid from coordindates from the original dataset
original_xy = np.mgrid[xmin:xmax + x_resolution:x_resolution, ymax + y_resolution:ymin:y_resolution]

# Create the figure (figsize is given in inches)
fig = plt.figure(figsize=(2*px_x*0.0104166667, 2*px_y*0.0104166667))

# Create basemap object
# Note: We choose mercator projection and only show map from original GeoTIFF file
bm = Basemap(projection='merc', lon_0=xmin, llcrnrlat=ymin, urcrnrlat=ymax, llcrnrlon=xmin, urcrnrlon=xmax, resolution='l')

# Create the projection objects for the conversion
# Get original projection
origin_proj = osr.SpatialReference()
origin_proj.ImportFromWkt(proj)
# Get target projection from Basemap object (projection argument)
target_proj = osr.SpatialReference()
target_proj.ImportFromProj4(bm.proj4string)

# Convert coordinates original_xy from original projection to target projection
converted_x, converted_y = convert_xy_projection(original_xy, origin_proj, target_proj)

# Plot data at coordinates converted_x and converted_y using a color map
bm.pcolormesh(converted_x, converted_y, data[0, :, :].T, cmap=plt.cm.gray)

# Draw coastlines on map
bm.drawcoastlines(linewidth=1)

# Reading excel from file and select sheet
df = pd.read_excel(filetoread[2], sheet_name='Sheet1')

# Retrieve dataframe columns latitude and lontitude
listLat = df['latitude']
listLon = df['longitude']

# Using basemap instance to convert lontitude and lattitude to position on the map
xlon, ylat = bm(listLon.tolist(), listLat.tolist())

# Plot the route as dots on the map
plt.plot(xlon, ylat, zorder=10, linewidth=0.5, alpha=1, color='Red')

# TODO: Retrieve current location (currently constant values on route) -> see gps_read.py file
xlon_me = 134.1791
ylat_me = -28.36473

# Using basemap instance to convert lontitude and lattitude to position on the map
xlon_me_map, ylat_me_map = bm(xlon_me, ylat_me)

# Plot the current location as a dot on the map
plt.plot(xlon_me_map, ylat_me_map, zorder=200, marker='+', alpha=1, markersize=4, color='Yellow')
plt.title("Australian cloud map")

plt.axis('off')

# Saving an image from the generated file
plt.savefig('world.png', dpi=72, bbox_inches='tight', pad_inches=0)
