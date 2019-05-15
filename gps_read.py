import serial
from sys import argv
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import re


ser = serial.Serial(port=argv[1], baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS, timeout=0)


print("Connected to port " + ser.portstr + ".")

count = 0
line = []

num_sats = 0
latitude = 0
longtitude = 0

fig = plt.figure(figsize=(20, 15))
bm = Basemap(projection='merc', llcrnrlat=-80, urcrnrlat=80, llcrnrlon=-180, urcrnrlon=180, lat_ts=20, resolution='l')

while ser.readable():
    if latitude != 0 and longtitude != 0:
        break

    for c in ser.read():
        line.append(c)
        if c == '\n':
            str_line = ''.join(line)
            comment_bool = re.search(r"^#.*$", str_line)
            if not comment_bool:
                gps_data = str_line.split()
                if len(gps_data) == 4:
                    if gps_data[0] == 'G':
                        num_sats = int(float(gps_data[1]))
                        latitude = float(gps_data[2])
                        longtitude = float(gps_data[3])

                        print('Connected to ' + str(num_sats) + ' satellites: ' + str(latitude) + ' ' + str(longtitude) + '')
            else:
                print(str_line[1:])
            line = []
            count += 1
            break

print("Disconnecting from port " + ser.portstr + ".")
ser.close()
bm.drawcoastlines(linewidth=0.1)
loc_x, loc_y = bm(longtitude, latitude)
plt.plot(loc_x, loc_y, zorder=200, marker='+', alpha=1, markersize=4, color='red')
plt.axis('off')
plt.savefig('gps_read.png', dpi=300, bbox_inches='tight', pad_inches=0)
plt.close()
