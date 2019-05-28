[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)
[![996.icu](https://img.shields.io/badge/link-996.icu-red.svg)](https://996.icu)

# CloudMap
CloudMap consists oftwo python programs for a bachelor project. The project consists of receiving images with EUMETCast. The most interesting images received on the basic service of EUMETCast are the MSG-1 weather images which are HRIT encoded. These images are converted into GeoTIFF images and processed into a cloud density image showing a route and GPS location.

For decompressing the HRIT images, GDAL is re-build with the msg driver enabled. The program that converts the HRIT files into GeoTIFF is the msg_to_geotiff.py file. Applying image processing and adding the route, coastlines, GPS location and datetime is done by geotiff_to_map.py. The route is taken from an Excel file and the GPS location from an Arduino with a GPS sensor.

<details>
<summary>CloudMap</summary>

   * [CloudMap](#cloudmap)
      * [msg_to_geotiff.py](#mtg)
          ** [Usage](#usage)
          ** [Examples](#examples)
      * [geotiff_to_map.py](#gtm)
          ** [Usage](#gtm-usage)
         
</details>

## msg_to_geotiff.py
To generate the exact python 2.7 environment used for this program one can find the _environment.yml_ file to create 
the python environment with Anaconda. Following packages are included:

- Basemap
- GDAL
- NumPy
- PyPlot
- Pandas
- Pillow

### Usage

`python geotiff_to_map.py [GeoTIFF] [Excel] [Gamma_correction{0|1}] [Temperature_intensity] [Brightness_intensity]`

### Examples
Example files are located inside the **examples** folder. To run these files take a look at the terminal examples 
below.

#### Generate example image without gamma correction
`geotiff_to_map.py examples\MSG_flat.tif examples\latlon_MSG.xlsx`

`geotiff_to_map.py examples\MSG_flat.tif examples\latlon_MSG.xlsx 0`

#### Generate example image with gamma correction and default intensity values
`geotiff_to_map.py examples\MSG_flat.tif examples\latlon_MSG.xlsx 1`

#### Generate example image with gamma correction and custom intensity values
`geotiff_to_map.py examples\MSG_flat.tif examples\latlon_MSG.xlsx 1 0.8 2`

## geotiff_to_map.py
To use this program GDAL has to be build with the MSG driver enabled.

### Usage
`python msg_to_geotiff.py [YYYYMMDDhhmm] [left] [top] [right] [bottom]`
