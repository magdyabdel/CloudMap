import os
import subprocess
from sys import argv
import glob
import math
import re
import errno

# Get working directory
CWD = os.getcwd()

# Version
VERS_MAJ = 1
VERS_MIN = 0

print("\033[93mMSG to GeoTIFF v" + str(VERS_MAJ) + "." + str(VERS_MIN) + "\033[0m\n")

str_usage = "Usage: msg_to_geotiff.py [YYYYMMDDhhmm] [left] [top] [right] [bottom]\n"

# Fix existing PROJ_LIB existance bug
removedPROJLIB = 0
ENV_VAR_PROJLIB = os.environ.get('PROJ_LIB')
if ENV_VAR_PROJLIB is not None:
    removedPROJLIB = 1
    del os.environ["PROJ_LIB"]

# Return the number of console arguments in a variable
argn = len(argv)

# Default values
arg_datetime = None
arg_left = None
arg_top = None
arg_right = None
arg_bottom = None


# mkdir -p implementation
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


# Get amount of digits for an integer
def get_digits(n):
    if n > 0:
        digits = int(math.log10(n)) + 1
    elif n == 0:
        digits = 1
    else:
        digits = int(math.log10(-n)) + 2
    return digits


# Check number of arguments passed
if argn == 2:
    arg_datetime = str(argv[1]) if get_digits(int(argv[1])) == 12 else None
    if arg_datetime is None:
        print(str_usage)
        exit(-1)
elif argn == 6:
    arg_datetime = str(argv[1]) if get_digits(int(argv[1])) == 12 else None
    arg_left = str(argv[2]) if -180 < argv[2] <= 180 else None
    arg_top = str(argv[3]) if -90 <= argv[3] <= 90 else None
    arg_right = str(argv[4]) if -180 < argv[4] <= 180 else None
    arg_bottom = str(argv[5]) if -90 <= argv[5] <= 90 else None
    if arg_datetime is None:
        print(str_usage)
        exit(-1)
    if None in (arg_left, arg_top, arg_right, arg_bottom):
        print(str_usage)
        print("Values exceed limits: -180 < longitude <= 180 and -90 <= latitude <= 90\n")
        exit(-1)
else:
    print(str_usage)
    exit(-1)

# Check if corresponding PRO file exists
PRO_file = glob.glob('*-PRO______-'+arg_datetime+'-__')
if not PRO_file:
    print("PRO file for " + arg_datetime + " does not exist.")
    exit(-1)

# Create directory structure
DIR_structure = os.path.join(CWD, arg_datetime[0:4], arg_datetime[4:6], arg_datetime[6:8])
try:
    mkdir_p(DIR_structure)
except OSError as exc:
    print(exc)
    exit(-1)

# Get all corresponding HRIT files in a list and rename them
HRIT_files = glob.glob('*-'+arg_datetime+'-*')
for i, HRIT_filename in enumerate(HRIT_files):
    HRIT_filename_new = re.sub(r'IODC', '____', HRIT_filename)
    os.rename(HRIT_filename, os.path.join(DIR_structure, HRIT_filename_new))
HRIT_files = None
PRO_file = None

# Filenames for GDAL
translate_output_file = arg_datetime + '_GEO.tif'
warp_output_file = arg_datetime + '_MERC.tif'

# If the output files already exist they are removed
try:
    fh = open(translate_output_file, 'r')
    fh.close()
    os.remove(translate_output_file)
except IOError as err:
    if err.errno != 2:
        print(err)
        exit(-1)
try:
    fh = open(warp_output_file, 'r')
    fh.close()
    os.remove(warp_output_file)
except IOError as err:
    if err.errno != 2:
        print(err)
        exit(-1)

# Get the geostationary image from the HRIT files
translate_sp = subprocess.call(["gdal_translate", "-a_srs",
                                "+proj=geos +h=35785831 +a=6378169 +b=6356583.8 +lon_0=41.5",
                                "-a_ullr", "-5568000", "5568000", "5568000", "-5568000", "-mask", "1", "-of", "GTiff",
                                "MSG(./,"+arg_datetime+",(4,9,10),N,B,1,1)", translate_output_file])
if translate_sp != 0:
    print("Something went wrong!")
    exit(-1)

# Get the mercator projected image from the geostationary image
if None not in (arg_left, arg_top, arg_right, arg_bottom):
    warp_sp = subprocess.call(["gdalwarp", "-te", arg_left, arg_bottom, arg_right, arg_top, "-te_srs", "EPSG:4326",
                               "-t_srs", "EPSG:4326", "-dstalpha", "-r", "lanczos", "-co", "COMPRESS=LZW",
                               translate_output_file, warp_output_file])
else:
    warp_sp = subprocess.call(["gdalwarp", "-te", "-te_srs", "EPSG:4326", "-t_srs", "EPSG:4326",
                               "-dstalpha", "-r", "lanczos", "-co", "COMPRESS=LZW", translate_output_file,
                               warp_output_file])
if warp_sp != 0:
    print("Something went wrong!")
    exit(-1)

# Remove geostationary projected GeoTIFF
keepGeostationary = 0
if not keepGeostationary:
    try:
        fh = open(translate_output_file, 'r')
        fh.close()
        os.remove(translate_output_file)
    except IOError as err:
        if err.errno != 2:
            print(err)
            exit(-1)

print("GeoTIFF with geostationary projection saved as " + translate_output_file + ".\n") if keepGeostationary else None
print("GeoTIFF with mercator projection saved as " + warp_output_file + ".\n")

# Add the PROJ_LIB environmental variable back again
if removedPROJLIB:
    os.environ['PROJ_LIB'] = ENV_VAR_PROJLIB

