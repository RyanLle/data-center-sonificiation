import pandas as pd
import matplotlib.pylab as plt
filename = 'Geospatial_Data_Centers_2026'

df = pd.read_csv(filename + '.csv')

lat = df['Latitude'].values
long = df['Longitude'].values
plt.scatter(lat, long, s=long)
plt.xlabel('Latitude')
plt.ylabel('Longitude')
plt.show()

def map_value(value, min_value, max_value, min_result, max_result):
    result = min_result + (value - min_value)/(max_value - min_value)*(max_result - min_result)
    return result

duration_beats = 52.8

t_data = map_value(long, 0, max(long), 0, duration_beats)

bpm = 60

duration_sec = duration_beats*60/bpm
print('Duration: ', duration_sec, ' seconds')
y_data = map_value(lat, 0, max(lat), 0, 1)
