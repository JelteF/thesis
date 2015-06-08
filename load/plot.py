from pprint import pprint  # noqa
import matplotlib.pyplot as plt  # noqa
import seaborn as sns  # noqa
import os
import json
import pandas as pd

sns.set_context("poster")
sns.set_palette("Paired")
palette = sns.color_palette("Paired")

BASE_PATH = os.path.abspath('data')
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

                    cur_d['requests_per_second'] = cur_d['requests'] / seconds
                    cur_d['MB/s'] = cur_d['bytes'] / 10**6 / seconds

                    for k, v in cur_d['latency'].items():
                        cur_d['latency' + '_' + k] = v

                    data.append(cur_d)
                    seconds = None

                elif len(l.split()) == 2:
                    k = l.split()[0][:-1]  # remove the collon
                    v = int(l.split()[-1])

                    cur_d[k] = v

                    if k == 'internal_bytes':
                        cur_d['Internally sent MB'] = v / 10**6


df = pd.DataFrame(data)
df.fillna(0, inplace=True)
print(df)
print(df[df.total_errors != 0])


def safe_filename(filename):
    return "".join([c for c in filename if c.isalpha() or c.isdigit() or
                    c in ' _-']).rstrip()


def saveplot(kind):
    # plt.show()
    plt.savefig('plots/' + safe_filename(' - '.join([run_type, prop, kind])) +
                '.png')
    plt.close()

setup_order = ['nocache.cdn', 'cdn', 'ismproxy', 'nocache.transmux',
               'single.transmux', 'double.transmux']

transmux_cache_order = setup_order[-2:]

for run_type, g in df.groupby('run_type'):
    extra_kwargs = {}
    if run_type == 'first_time':
        bar_order = setup_order[2:] + setup_order[:2]
        print(g.max())
    elif run_type == 'second_time':
        bar_order = transmux_cache_order + ['cdn']
    elif run_type == 'after_other':
        extra_kwargs['col'] = 'after'
        bar_order = transmux_cache_order

    plot_vals = ['MB/s', 'Internally sent MB', 'internal_requests',
                 'requests_per_second', 'cache_usage', 'latency_mean']
    # plot_vals = ['latency_mean']
    for prop in plot_vals:
        if prop in ['MB/s', 'requests_per_second', 'latency_mean']:
            if 'col' not in extra_kwargs:
                vid_type_key = 'col'
            else:
                vid_type_key = 'row'
            extra_kwargs[vid_type_key] = 'video_type'

            sns.factorplot('connections', prop, 'server_type', kind='point',
                           data=g, sharey=True,
                           hue_order=bar_order, palette=palette,
                           **extra_kwargs)
            saveplot('point')
            del extra_kwargs[vid_type_key]

        else:
            sns.factorplot('video_type', prop, 'server_type', kind='bar',
                           data=g, sharey=True,
                           hue_order=bar_order, palette=palette,
                           **extra_kwargs)
            saveplot('bar')
