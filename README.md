[![996.icu](https://img.shields.io/badge/link-996.icu-red.svg)](https://996.icu)

# CloudMap
CloudMap is a python project for EE5. It converts GeoTIFF files into images where a route (based on an Excel file) and 
the current location is plotted on.

## Usage
To generate the exact environment used for this project one can find the _environment.yml_ file to create the python 
environment with Anaconda. Following packages are included:
- Basemap
- GDAL
- NumPy
- PyPlot
- Pandas

The script has to be executed as follows: 
`python geotiff_to_map.py [GeoTIFF_file] [Excel_file]`

Note: For testing purposes the GeoTIFF file can be _test.tif_ and the Excel file can be _latlon.xlsx_ which are provided
inside this project.
