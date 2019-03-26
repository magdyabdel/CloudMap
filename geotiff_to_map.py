# -*- coding: utf-8 -*-
from mpl_toolkits.basemap import Basemap
import osr, gdal
import numpy as np
from sys import argv
import matplotlib.pyplot as plt
import pandas as pd

filetoread = argv


def convertXY(xy_source, inproj, outproj):
    # function to convert coordinates

    shape = xy_source[0, :, :].shape
    size = xy_source[0, :, :].size

    # the ct object takes and returns pairs of x,y, not 2d grids
    # so the the grid needs to be reshaped (flattened) and back.
    ct = osr.CoordinateTransformation(inproj, outproj)
    xy_target = np.array(ct.TransformPoints(xy_source.reshape(2, size).T))

    xx = xy_target[:, 0].reshape(shape)
    yy = xy_target[:, 1].reshape(shape)

    return xx, yy


# Read the data and metadata
ds = gdal.Open(filetoread[1])

data = ds.ReadAsArray()
gt = ds.GetGeoTransform()
proj = ds.GetProjection()

xres = gt[1]
yres = gt[5]

# get the edge coordinates and add half the resolution
# to go to center coordinates
xmin = gt[0] + xres * 0.5
xmax = gt[0] + (xres * ds.RasterXSize) - xres * 0.5
ymin = gt[3] + (yres * ds.RasterYSize) + yres * 0.5
ymax = gt[3] - yres * 0.5

print('min X = ', xmin)
print('max X = ', xmax)
print('min Y = ', ymin)
print('max Y = ', ymax)

ds = None

# create a grid of xy coordinates in the original projection
xy_source = np.mgrid[xmin:xmax+xres:xres, ymax+yres:ymin:yres]
print("figure")
# Create the figure and basemap object
fig = plt.figure(figsize=(20, 20))
# m = Basemap(projection='ortho', lon_0=xmin+(xmax-xmin)/2, lat_0=ymin+(ymax-ymin)/2, resolution='l')
m = Basemap(projection='ortho', lon_0=141.17, lat_0=2.177, resolution='l')

# Create the projection objects for the convertion
# original (Albers)
inproj = osr.SpatialReference()
inproj.ImportFromWkt(proj)

# Get the target projection from the basemap object
outproj = osr.SpatialReference()
outproj.ImportFromProj4(m.proj4string)

print("Convert XY")
# Convert from source projection to basemap projection
xx, yy = convertXY(xy_source, inproj, outproj)
print("Plotting data")
# plot the data (first layer)
im1 = m.pcolormesh(xx, yy, data[0, :, :].T, cmap=plt.cm.gray)
# im1 = m.contourf(xx, yy, data[0, :, :].T, 20, cmap=plt.cm.gray)

# annotate
m.drawcoastlines(linewidth=.1)

print("Reading excel")

# Reading excel
df = pd.read_excel(filetoread[2], sheet_name='Sheet1')

listLat = df['latitude']
listLon = df['longitude']

xlon, ylat = m(listLon.tolist(), listLat.tolist())

plt.scatter(xlon, ylat, zorder=10, s=0.1, alpha=1, marker='.', color='Red')

xlon_me = 134.1791
ylat_me = -28.36473

xlon_me_map, ylat_me_map = m(xlon_me, ylat_me)
m.plot(xlon_me_map, ylat_me_map, zorder=15, marker='.', alpha=1, markersize=0.1, color='Blue')

plt.savefig('world.png', dpi=300)

print('saved')