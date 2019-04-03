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

    # Reshape: Reshape the source_xy to a mxn (bm=2, n=size) matrix and transpose it
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

# Return minimum and maximum coordinates of the GeoTIFF image
# Note: RasterXSize and RasterYSize return the raster width and height in pixels
# Note: Adding or removing half the resolution is a small correction
xmin = gt[0] + x_resolution * 0.5
xmax = gt[0] + (x_resolution * geo_dataset.RasterXSize) - x_resolution * 0.5
ymin = gt[3] + (y_resolution * geo_dataset.RasterYSize) + y_resolution * 0.5
ymax = gt[3] - y_resolution * 0.5

# Clear dataset
geo_dataset = None

# Create a dense meshgrid from coordindates from the original dataset
original_xy = np.mgrid[xmin:xmax + x_resolution:x_resolution, ymax + y_resolution:ymin:y_resolution]

# Create the figure (figsize is given in inches)
fig = plt.figure(figsize=(20, 20))

# Create basemap object
# Note: We center the orthogonala projection with lon_0 and lat_0
bm = Basemap(projection='ortho', lon_0=xmin+(xmax-xmin)/2, lat_0=ymin+(ymax-ymin)/2, resolution='l')

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
bm.drawcoastlines(linewidth=.1)

# Reading excel from file and select sheet
df = pd.read_excel(filetoread[2], sheet_name='Sheet1')

# Retrieve dataframe columns latitude and lontitude
listLat = df['latitude']
listLon = df['longitude']

# Using basemap instance to convert lontitude and lattitude to position on the map
xlon, ylat = bm(listLon.tolist(), listLat.tolist())

# Plot the route as dots on the map
plt.scatter(xlon, ylat, zorder=10, s=0.1, alpha=1, marker=',', color='Red')

# TODO: Retrieve current location (currently constant values on route)
xlon_me = 134.1791
ylat_me = -28.36473

# Using basemap instance to convert lontitude and lattitude to position on the map
xlon_me_map, ylat_me_map = bm(xlon_me, ylat_me)

# Plot the current location as a dot on the map
bm.plot(xlon_me_map, ylat_me_map, zorder=30, marker='.', alpha=1, markersize=0.1, color='Yellow')

# Saving an image from the generated file
plt.savefig('world.png', dpi=300)
