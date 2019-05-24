[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)
[![996.icu](https://img.shields.io/badge/link-996.icu-red.svg)](https://996.icu)

# CloudMap
CloudMap is a python program part of a project. The project consists of receiving images with EUMETCast. The most 
interesting images received on the basic service are the MSG1 weather images.

CloudMap is converts GeoTIFF images into map images where a route (based on an Excel file) and the current location 
is plotted on. The used GeoTIFF images are generated using a custom build GDAL version which implements the MSG driver
(which is not included by default). 

<details>
<summary>Index</summary>

   * [CloudMap](#cloudmap)
      * [Usage](#usage)
      * [Examples](#examples)
         
</details>

## Usage
To generate the exact python 2.7 environment used for this project one can find the _environment.yml_ file to create 
the python environment with Anaconda. Following packages are included:

- Basemap
- GDAL
- NumPy
- PyPlot
- Pandas
- Pillow

Usage: `geotiff_to_map.py [GeoTIFF] [Excel] [Gamma_correction{0|1}] [Temperature_intensity] [Brightness_intensity]`

## Examples
Example files are located inside the examples folder. To run these files take a look at the example terminal usages 
below.

### Generate example image without gamma correction
`geotiff_to_map.py "examples\MSG_flat.tif" "examples\latlon_MSG.xlsx"`
or `geotiff_to_map.py "examples\MSG_flat.tif" "examples\latlon_MSG.xlsx" 0`

### Generate example image with gamma correction and default intensity values
`geotiff_to_map.py "examples\MSG_flat.tif" "examples\latlon_MSG.xlsx" 1`

### Generate example image with gamma correction and custom intensity values
`geotiff_to_map.py "examples\MSG_flat.tif" "examples\latlon_MSG.xlsx" 1 0.8 2`