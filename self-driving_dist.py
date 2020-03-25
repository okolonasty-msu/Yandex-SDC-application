import json
import numpy as np
import pandas as pd
import sys
import urllib

data_j = []
# URL = sys.argv[1]
URL = 'https://sdcimages.s3.yandex.net/test_task/data'
with urllib.request.urlopen(URL) as j:
    for line in j:
        data_j.append(json.loads(line))

data_j.sort(key=lambda log: log['ts'])

control_switch_on = None
lat = None
lon = None
normalized_data = []
for log in data_j:
    if ('geo' in log) and control_switch_on is not None:
        if log['geo']['lat'] == 0.0:
            continue
        lat = log['geo']['lat']
        lon = log['geo']['lon']
        normalized_data.append({'lat': log['geo']['lat'],
                                'lon': log['geo']['lon'],
                                'control_switch_on': control_switch_on,
                                'ts': log['ts']})
    elif 'control_switch_on' in log and lat is not None and lon is not None:
        control_switch_on = log['control_switch_on']
        normalized_data.append({'lat': lat,
                                'lon': lon,
                                'control_switch_on': log['control_switch_on'],
                                'ts': log['ts']})
    elif lat is None and lon is None:
        lat = log['geo']['lat']
        lon = log['geo']['lon']

data_new = pd.DataFrame.from_dict(normalized_data)

# Calculating dist on each time interval

lat = np.radians(np.array(data_new['lat']))
lon = np.radians(np.array(data_new['lon']))
dlat = lat[1:] - lat[:-1]
dlon = lon[1:] - lon[:-1]
tmp = np.sin(dlat / 2) ** 2 + np.cos(lat[1:]) * np.cos(lat[:-1]) * np.sin(dlon / 2) ** 2
dists = 2 * 6371 * np.arcsin(np.sqrt(tmp))

# Calculating SD and Manual total dists
a, b = pd.DataFrame({
    'dist': dists,
    'control_switch_on': data_new['control_switch_on'][:-1]
}).groupby(by='control_switch_on')['dist'].sum()

# another way:
# dists[data_new['control_switch_on'][:-1]].sum()

print(f'''Manual mode dist: {a:.3f} km.
Self-driving mode dist: {b:.3f} km.''')
