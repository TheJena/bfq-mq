#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0

import argparse
import numpy
from matplotlib import pyplot
from scipy import stats

def parse_duration(record):
    if '%' not in record:
        record += ' 0.00%'
    rec = record.split()
    return {'location': ''.join(rec[:1]),
            'prefix': ' '.join(rec[1:2]),
            'message': ' '.join(rec[2:-3]),
            't_delta_ns': int(rec[-3:-2][0]),
            't_delta_%': float(rec[-1:][0].strip('%'))}

output_formats = ('png', 'pdf', 'ps', 'eps', 'svg')
parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''Given a trace summary like:
    src-file.c  +line_num  . root_function       4144 ns
    src-file.c  +line_num  `-- sub_function_1      89 ns     2.15%
    src-file.c  +line_num  `-- sub_function_2     303 ns     7.31%
    src-file.c  +line_num  `-- sub_function_3     442 ns    10.67%
    ...          ...           ...                ...        ...

And a function name (e.g. 'sub_function_3'), this script will
plot the probability distribution of its execution time and
print some statistics.''')
parser.add_argument(dest='input_file',
                    help='trace summary',
                    metavar='trace_summary.txt',
                    type=open)
parser.add_argument('-o', '--output',
                    default=None,
                    dest='output_file',
                    help='save plot to output file ' +
                         repr(output_formats).replace("'", ''),
                    metavar='svg',
                    required=False,
                    type=str)
parser.add_argument('-m', '--min-cdf',
                    dest='x_min',
                    help='set minimum value on x-axis to the value in which '
                         'the cumulative-distribution-function of the random '
                         'variable (function execution time) is q',
                    metavar='q',
                    required=False,
                    type=float)
parser.add_argument('-M', '--max-cdf',
                    dest='x_max',
                    help='set maximum value on x-axis to the value in which '
                         'the cumulative-distribution-function of the random '
                         'variable (function execution time) is q',
                    metavar='q',
                    required=False,
                    type=float)
parser.add_argument('-p', '--points',
                    default=16384,
                    dest='points',
                    help='number of points used to plot the distribution ',
                    metavar='int',
                    type=int)
parser.add_argument('-r', '--use-root-fn',
                    action='store_true',
                    dest='use_root_fn',
                    help='filter root functions instead of child ones')
parser.add_argument(dest='fun_name',
                    help='function whose execution time probability '
                         'distribution will be plot',
                    metavar='function_name',
                    type=str)
ARGS = parser.parse_args()

if ARGS.output_file and ARGS.output_file.split('.')[-1] not in output_formats:
    raise ValueError('Output format not supported, '
                     'please use one of the following ones: '
                     + repr(output_formats).replace("'", '')[1:-1] + '.')

data = list()
for line in ARGS.input_file:
    if 'ns' not in line:
        continue
    l = parse_duration(line)
    if l['message'] == ARGS.fun_name:
        if ARGS.use_root_fn == bool(l['prefix'] == '.'):
            data.append(l['t_delta_ns'])

if not data:
    raise ValueError('function "{}" not found in {}'.format(ARGS.fun_name,
                                                            ARGS.input_file))

data = numpy.array(data)
distribution = stats.rv_histogram(
    numpy.histogram(data, bins=numpy.arange(data.min(), data.max(), step=1),
                    density=True))

mean, std = distribution.mean(), distribution.std()
Q1, Q2, Q3 = distribution.ppf([0.25, 0.50, 0.75]) # percent point function
IQR = Q3 - Q1 # interquartile range

vbars=dict()
print('Statistics of "{}":'.format(ARGS.fun_name))
for lab, val in zip(('Q1 - 1.5 x IQR', 'Q1', 'median', 'Q3', 'Q3 + 1.5 x IQR'),
                    (Q1 - 1.5 * IQR, Q1, Q2, Q3, Q3 + 1.5 * IQR)):
    print('{} {:.3f} ns'.format(str(lab + ':').ljust(16), val))
    vbars[lab] = val
print('{} {:.3f} ns ± {:.3f} ns'.format('mean ± std:'.ljust(16), mean, std))

vbars['mean'] = mean
vbars['min'] = data.min()
vbars['max'] = data.max()

plot_from = max(data.min(), Q1 - 1.5 * IQR)
plot_to = min(data.max(), max(mean, Q3 + 1.5 * IQR))
if ARGS.x_min:
    plot_from = distribution.ppf(ARGS.x_min)
    vbars['  '] = distribution.ppf(ARGS.x_min)
if ARGS.x_max:
    plot_to = distribution.ppf(ARGS.x_max)
    vbars[' '] = distribution.ppf(ARGS.x_max)

fig = pyplot.figure()
middle = fig.add_subplot(111) # (middle x-axis)
bottom_x_axis = middle.twiny() # quartiles
top_x_axis = middle.twiny() # cumulative distribution function

# adjust title, axes labels and axes positions
pyplot.title('Probability distribution of "{}" '.format(ARGS.fun_name) +
             'execution time\n({})\n\n\n'.format(ARGS.input_file.name))
top_x_axis.set_xlabel('cumulative distribution')
top_x_axis.xaxis.set_label_coords(0.95, 1.05)
middle.set_xlabel('[ns]')
middle.xaxis.set_label_coords(0.99, -0.02)
bottom_x_axis.spines['bottom'].set_position(('axes', -0.07))
bottom_x_axis.xaxis.set_ticks_position('bottom')
bottom_x_axis.spines['bottom'].set_visible(True)

# adjust axes ticks and tick labels
top_x_axis.set_xticks(list(vbars.values()))
top_x_axis.set_xticklabels(
    ['{:.2f}'.format(distribution.cdf(t)) for t in vbars.values()])
bottom_x_axis.set_xticks(list(vbars.values()))
bottom_x_axis.set_xticklabels(list(vbars.keys()), rotation=45)

# plot probability density function
X = numpy.linspace(data.min(), data.max(), min(ARGS.points, data.shape[0]))
middle.plot(X, distribution.pdf(X), color='blue', linewidth=1)
y_limits = middle.get_ylim() # save current y-axis limits

# plot vertical dashed lines
middle.vlines(list(vbars.values()), *y_limits, linewidth=0.7, linestyle='--')

middle.set_ylim(y_limits) # forced saved y-axis limits
for ax in (middle, bottom_x_axis, top_x_axis):
    ax.set_xlim((plot_from, plot_to))

fig.set_size_inches(16.5, 9.4)
fig.subplots_adjust(bottom=0.2, top=0.85)
if ARGS.output_file:
    fig.savefig(ARGS.output_file, dpi=96)
else:
    pyplot.show()
