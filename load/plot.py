from pprint import pprint  # noqa
import matplotlib.pyplot as plt  # noqa
import seaborn as sns  # noqa
import os
import json
import pandas as pd

sns.set_context("poster")

BASE_PATH = os.path.abspath('data_new')
dirs = os.listdir(BASE_PATH)
data = []
for d in dirs:
    dir_path = os.path.join(BASE_PATH, d)
    for filename in os.listdir(dir_path):
        if not filename.endswith('.log'):
            continue

        video_type = '-'.join(filename.split('-')[1:3])
        file_path = os.path.join(dir_path, filename)
        with open(file_path) as f:
            after = None
            run_type = None
            seconds = None
            cur_d = None
            for l in f:
                if l.startswith('run_type'):
                    run_type = l.split()[-1]
                    after = None
                elif l.startswith('after'):
                    after = l.split()[-1].split('-')[1]

                elif l.startswith('elapsed time'):
                    seconds = float(l.split()[-1])

                elif l.startswith('summary'):
                    cur_d = json.loads(l.split()[-1])
                    cur_d['server_type'] = d
                    cur_d['video_type'] = video_type[5:]
                    cur_d['run_type'] = run_type
                    cur_d['after'] = after

                    if seconds is None:
                        seconds = cur_d['duration'] / 10**6
                    cur_d['seconds'] = seconds

                    print(type(cur_d['requests']))
                    print(seconds)
                    cur_d['requests_per_second'] = cur_d['requests'] / seconds
                    cur_d['MB/s'] = cur_d['bytes'] / 10**6 / seconds

                    data.append(cur_d)
                    seconds = None

                elif len(l.split()) == 2:
                    k = l.split()[0][:-1]  # remove the collon
                    v = int(l.split()[-1])

                    cur_d[k] = v


df = pd.DataFrame(data)
df.fillna(0, inplace=True)
print(df)

for run_type, g in df.groupby('run_type'):
    print(run_type)
    print(g.max())
    continue
    for prop in ['MB/s', 'internal_bytes', 'internal_requests']:
        sns.factorplot('video_type', prop, 'server_type', kind='bar',
                       data=g, sharey=False)
        plt.title(run_type)
        plt.show()
