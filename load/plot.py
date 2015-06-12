from pprint import pprint  # noqa
import matplotlib.pyplot as plt  # noqa
import seaborn as sns  # noqa
import os
import json
import pandas as pd
from pylatex import Figure

sns.set_style('whitegrid', rc={'lines.solid_capstyle': 'butt'})
sns.set_context("paper", rc={"lines.linewidth": 0.55})
sns.set_palette("Paired")
palette = sns.color_palette("Paired")

BASE_PATH = os.path.abspath('data_100mbit')
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
                    cur_d['mbps'] = cur_d['bytes'] / 10**6 / seconds

                    for k, v in cur_d['latency'].items():
                        cur_d['latency' + '_' + k] = v / 1000

                    data.append(cur_d)
                    seconds = None

                elif len(l.split()) == 2:
                    k = l.split()[0][:-1]  # remove the collon
                    v = int(l.split()[-1])

                    cur_d[k] = v

                    if k == 'internal_bytes':
                        cur_d['internal_mb'] = v / 10**6
                    if k == 'cache_usage':
                        # Covert blocks to mb
                        cur_d['cache_usage'] = v * 1024 / 10**6


df = pd.DataFrame(data)
df.fillna(0, inplace=True)
# print(df)
# print(df[df.total_errors != 0])
server_type_dict = {
    'ismproxy': 'IPP',
    'cdn': 'CDN',
    'single.transmux': 'LT-single',
    'double.transmux': 'LT-double',
    'nocache.transmux': 'LT-nocache',
    'nocache.cdn': 'CDN-nocache',
}
df.replace({'server_type': server_type_dict}, inplace=True)
df.video_type = df.video_type.str.upper()
df.after = df.after.str.upper()
df.rename(columns={'server_type': 'Server setup'}, inplace=True)


def safe_filename(filename):
    return "".join([c for c in filename if c.isalpha() or c.isdigit() or
                    c in ' _-']).rstrip()


def saveplot():
    # plt.show()
    filename = 'plots/' + safe_filename('_'.join([run_type, prop]))
    plt.savefig(filename + '.pdf')

    plt.close()

    fig = Figure()
    fig.add_image(filename + '.pdf')
    fig.add_caption(labels[prop] + ' with ' + run_type_labels[run_type])
    fig.append(r'\label{fig:' + filename.split('/')[-1] + '}')
    fig.generate_tex(filename)


setup_order = ['CDN-nocache', 'CDN', 'IPP', 'LT-nocache', 'LT-single',
               'LT-double']

transmux_cache_order = setup_order[-2:]

labels = {
    'mbps': 'Received MB/s',
    'internal_mb': 'Internally sent MB',
    'internal_requests': 'Amount of internal requests',
    'requests_per_second': 'Handled requests per second',
    'cache_usage': 'Cache usage in MB',
    'latency_mean': 'Average latency in ms',
}

run_type_labels = {
    'first_time': 'a cold cache',
    'second_time': 'the cache filled with the same format',
    'after_other': 'the cache filled with another format',
}

col_wrap = 2
for run_type, g in df.groupby('run_type'):
    extra_kwargs = {'size': 2}
    point_title_format = 'Requested {col_name}'
    if run_type == 'first_time':
        bar_order = setup_order[2:] + setup_order[:2]

    elif run_type == 'second_time':
        bar_order = transmux_cache_order + ['CDN']
    elif run_type == 'after_other':
        extra_kwargs['col'] = 'after'
        bar_order = transmux_cache_order
        bar_title_format = 'Requested {col_var} {col_name}'
        point_title_format = 'Requested {row_name} {col_var} {col_name}'

    plot_vals = ['mbps', 'internal_mb', 'internal_requests',
                 'requests_per_second', 'cache_usage', 'latency_mean']
    plot_vals = ['latency_mean']
    for prop in plot_vals:
        print(run_type, prop)
        if prop in ['mbps', 'requests_per_second', 'latency_mean']:
            if 'col' not in extra_kwargs:
                vid_type_key = 'col'
            else:
                vid_type_key = 'row'
                col_wrap = None
            extra_kwargs[vid_type_key] = 'video_type'

            p = sns.factorplot('connections', prop, 'Server setup',
                               kind='point', data=g, sharey=True,
                               sharex=False, hue_order=bar_order,
                               palette=palette, col_wrap=col_wrap,
                               **extra_kwargs)

            p.set_titles(point_title_format)
            p.set_xlabels('Concurrent connections')
            p.set_ylabels(labels[prop])

            if prop == 'latency_mean':
                for ax in p.fig.get_axes():
                    ax.set_yscale('log')

            saveplot()

            del extra_kwargs[vid_type_key]
            col_wrap = 2

        else:
            aspect = 1
            if 'col' not in extra_kwargs:
                aspect = 1.5
                col_wrap = None

            p = sns.factorplot('video_type', prop, 'Server setup', kind='bar',
                               data=g, sharey=True, sharex=False,
                               hue_order=bar_order, palette=palette,
                               col_wrap=col_wrap,
                               aspect=aspect,
                               **extra_kwargs)
            p.set_titles(bar_title_format)
            p.set_xlabels('Requested video format')
            p.set_ylabels(labels[prop])
            saveplot()
            col_wrap = 2
