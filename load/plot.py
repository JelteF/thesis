from pprint import pprint  # noqa
import numpy as np
import matplotlib.pyplot as plt  # noqa
import seaborn as sns  # noqa
import os
import json
from collections import defaultdict
import pandas as pd

sns.set_context("poster")

BASE_PATH = os.path.abspath('data')
dirs = os.listdir(BASE_PATH)
data = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
for d in dirs:
    dir_path = os.path.join(BASE_PATH, d)
    for filename in os.listdir(dir_path):
        if not filename.endswith('.log'):
            continue

        video_type = '-'.join(filename.split('-')[1:3])
        file_path = os.path.join(dir_path, filename)
        with open(file_path) as f:
            cur_d = data[d][video_type]
            lines = f.readlines()
            initial_seconds = float(lines[2].split()[-1])
            summaries = {
                'initial': json.loads(lines[3].split()[-1]),
                'next': json.loads(lines[6].split()[-1]),
            }

            cur_d['initial']['seconds'] = initial_seconds
            cur_d['next']['seconds'] = summaries['next']['duration'] / 10**6

            for k, summary in summaries.items():
                sec = cur_d[k]['seconds']
                cur_d[k]['requests'] = summary['requests']
                cur_d[k]['requests_per_sec'] = summary['requests'] / sec
                bytes_ = summary['bytes']
                cur_d[k]['bytes'] = bytes_
                cur_d[k]['mbps'] = summary['bytes'] / 10**6 / sec


l = []
for server_type, server_data in data.items():
    new_server_data = {}
    for video_type, video_data in server_data.items():
        for test_type, test_data in video_data.items():
            for k, v in test_data.items():
                l.append([server_type, video_type[5:], test_type, k, v])


df = pd.DataFrame.from_records(l, columns=['server', 'video', 'test',
                                           'property', 'value'])
print(df)
for name, g in df.groupby('property'):
    if name in ['requests_per_sec', 'mbps']:
        name = name.replace('_', ' ')
        g = g.rename(columns={'value': name})
        sns.factorplot('video', name, 'server', row='test', kind='bar',
                       data=g, sharey=False)
        plt.show()

#
# pprint(new_data)
#
# order = sorted(new_data['basic'].keys())
# pprint(order)
#
# request_ps_data = {}
#
# for server_type, server_data in new_data.items():
#     l = []
#     request_ps_data[server_type] = l
#     for test_type in order:
#         l.append(server_data[test_type]['requests_per_sec'])
#
# pprint(request_ps_data)
#
# bar_width = 0.25
# fig = plt.figure()
# ax = fig.gca()
# bargroup_starts = np.arange(len(order)) * 2
# for i, (server_type, server_data) in enumerate(request_ps_data.items()):
#     print(i, l)
#     rects = ax.bar(bargroup_starts + i*bar_width, server_data)
#
# plt.show()
