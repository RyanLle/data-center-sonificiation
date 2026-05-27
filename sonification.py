import pandas as pd
import matplotlib.pylab as plt
filename = 'Geospatial_Data_Centers_2026'

df = pd.read_csv(filename + '.csv')

# use the exact 'lat' and 'lng' columns and keep only rows with both numeric values (pairs stay aligned)
coords = df[['lat', 'lng']].apply(pd.to_numeric, errors='coerce').dropna()
if coords.empty:
    raise ValueError("No valid numeric coordinate pairs found in 'lat' and 'lng' columns.")

lat = coords['lat'].values
lon = coords['lng'].values

# vertical translation only: shift so the minimum becomes zero (preserves relative geometry)
lat_shift = -lat.min() if lat.min() < 0 else 0.0
lon_shift = -lon.min() if lon.min() < 0 else 0.0
lat = lat + lat_shift
lon = lon + lon_shift

# ensure marker sizes are positive
sizes = (lon - lon.min()) + 1.0

plt.scatter(lon, lat, s=sizes)
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.show()

def map_value(value, min_value, max_value, min_result, max_result):
    denom = max_value - min_value
    if denom == 0:
        return (min_result + max_result) / 2.0
    return min_result + (value - min_value)/denom*(max_result - min_result)

duration_beats = 52.8

t_data = map_value(lon, lon.min(), lon.max(), 0, duration_beats)

bpm = 60

duration_sec = duration_beats*60/bpm
print('Duration: ', duration_sec, ' seconds')
y_data = map_value(lat, lat.min(), lat.max(), 0, 1)
