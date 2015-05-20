from pprint import pprint  # noqa
import matplotlib.pyplot as plt  # noqa
import seaborn as sns  # noqa
import os
import json
from collections import defaultdict

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

