# -*- coding: utf-8 -*-
import osr
import numpy as np


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

