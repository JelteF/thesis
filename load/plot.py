from pprint import pprint  # noqa
import matplotlib.pyplot as plt  # noqa
import seaborn as sns  # noqa
import os
import json
import pandas as pd
from matplotlib.collections import PathCollection
import numpy as np
from pylatex import Figure
from pylatex.base_classes import Options, Command

sns.set_style('whitegrid', rc={'lines.solid_capstyle': 'butt'})
sns.set_context("paper", rc={"lines.linewidth": 0.55})
pal_large = sns.color_palette("Paired")
pal_large = pal_large[4:] + pal_large[:4]
pal_small = pal_large[2:]
pal_small.pop(2)

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
    fig.append(r'\centering')
    img_opts = Options(keepaspectratio='true', height=r'0.8\textheight',
                       width=r'\textwidth')
    fig.append(Command('includegraphics', options=img_opts,
                       arguments=filename + '.pdf'))
    fig.add_caption(labels[prop] + ' met ' + run_type_labels[run_type])
    fig.append(r'\label{fig:' + filename.split('/')[-1] + '}')
    fig.generate_tex(filename)


setup_order = ['CDN-nocache', 'CDN', 'IPP', 'LT-nocache', 'LT-single',
               'LT-double']

transmux_cache_order = setup_order[-2:]

labels = {
    'mbps': 'Ontvangen MB/s',
    'internal_mb': 'Intern gestuurde MB',
    'internal_requests': 'Aantal interne requests',
    'requests_per_second': 'Aantal requests per seconde',
    'cache_usage': 'Cache gebruik in MB',
    'latency_mean': 'Gemiddelde latency in ms',
}

run_type_labels = {
    'first_time': 'een lege cache',
    'second_time': 'een cache gevuld met hetzelfde formaat',
    'after_other': 'een cache gevuld met een ander formaat',
}

video_type_order = ['DASH', 'ISS', 'HDS', 'HLS']

point_plots = ['mbps', 'requests_per_second', 'latency_mean']

col_wrap = 2
for run_type, g in df.groupby('run_type'):
    extra_kwargs = {'size': 2}
    point_title_format = '{col_name} opgevraagd'
    if run_type == 'first_time':
        bar_order = setup_order[2:] + setup_order[:2]
        palette = pal_large

    elif run_type == 'second_time':
        bar_order = transmux_cache_order + ['CDN']
        palette = pal_small
    elif run_type == 'after_other':
        extra_kwargs['col'] = 'after'
        extra_kwargs['col_order'] = video_type_order
        bar_order = transmux_cache_order + ['CDN']
        bar_title_format = 'Opgevraagd na {col_name}'
        point_title_format = '{row_name} opgevraagd na {col_name}'
        palette = pal_small

    plot_vals = ['mbps', 'internal_mb', 'internal_requests',
                 'requests_per_second', 'cache_usage', 'latency_mean']
    # plot_vals = ['latency_mean']
    for prop in plot_vals:
        print(run_type, prop)
        if prop in point_plots:
            if 'col' not in extra_kwargs:
                vid_type_key = 'col'
            else:
                vid_type_key = 'row'
                col_wrap = None
            extra_kwargs[vid_type_key] = 'video_type'
            extra_kwargs[vid_type_key + '_order'] = video_type_order

            p = sns.factorplot('connections', prop, 'Server setup',
                               kind='point', data=g, sharey=True,
                               sharex=False, hue_order=bar_order,
                               palette=palette, col_wrap=col_wrap,
                               **extra_kwargs)

            p.set_titles(point_title_format)
            p.set_xlabels('Gelijktijdige connecties')
            p.set_ylabels(labels[prop])

            nums = [1, 2, 5, 10, 25, 50]
            np_nums = np.array(nums).reshape((6, 1))
            for ax in p.fig.get_axes():
                for line in ax.get_lines():
                    l = []
                    for x in line.get_xdata():
                        l.append(nums[int(x)])
                    line.set_xdata(l)

                for path in ax.get_children():
                    if isinstance(path, PathCollection):
                        offsets = path.get_offsets()

                        offsets[:, :1] = np_nums
                        path.set_offsets(offsets)

                ax.set_xscale('log')
                ax.set_xlim(xmin=0.5, xmax=100)

            if prop == 'latency_mean':

                for ax in p.fig.get_axes():
                    ax.set_yscale('log')
                    ax.set_ylim(ymin=1)

            else:
                p.set(ylim=(0, None))

            saveplot()

            del extra_kwargs[vid_type_key]
            del extra_kwargs[vid_type_key + '_order']
            col_wrap = 2

        else:
            aspect = 1
            if 'col' not in extra_kwargs:
                aspect = 1.5
                col_wrap = None

            p = sns.factorplot('video_type', prop, 'Server setup', kind='bar',
                               data=g, sharey=True, sharex=False,
                               x_order=video_type_order,
                               hue_order=bar_order, palette=palette,
                               col_wrap=col_wrap,
                               aspect=aspect,
                               **extra_kwargs)
            p.set_titles(bar_title_format)
            p.set_xlabels('Opgevraagde video formaat')
            p.set_ylabels(labels[prop])
            p.set(ylim=(0, None))
            saveplot()
            col_wrap = 2
