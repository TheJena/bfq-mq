#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0

import argparse

def parse_duration(record):
    rec = record.split()
    offset = int(bool(rec[1] == '+'))
    return {'location': ''.join(rec[:2+offset]),
            'message': ' '.join(rec[2+offset:-3]),
            't_delta_ns': int(rec[-2:-1][0])}

parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""\
    Script main features are:
    - filter from the given trace only bfq-mq time deltas lines
    - drop root-function with time delta lesser than the given
      one (default: 1 ns)
    - drop sub-functions with time delta lesser than the given
      percentage of the parent root-function (default: 0.01)
    - add to the measured sub-functions a column with the
      respective percentage of the total parent root-function

    For a better output alignment it is recommended to append
    to the script invocation a bash pipeline like:
    $ ... script invocation ... | column -s$'\\t' -t | sed "s/^#*//"
""")
parser.add_argument(help='/sys/kernel/debug/tracing/trace',
                    metavar='trace',
                    type=open,
                    dest='input_file')
parser.add_argument('--t-delta-min',
                    help="Filter functions which parent' execution time is at "
                         "least t_delta ns (default=1)",
                    metavar='ns',
                    type=int,
                    default=1,
                    dest='min_t_delta')
parser.add_argument('--min-percentage',
                    help='Filter functions whose execution time is at least '
                         'the specified fraction of the parent (default=0.01)',
                    metavar='%',
                    type=float,
                    default=0.01,
                    dest='min_percentage')
ARGS = parser.parse_args()

trace = list()
for line in ARGS.input_file.readlines():
    if 'block/' not in line:
        continue
    line = line.split('block/')[1]

    if 't_delta' in line:
        trace.append(parse_duration(line))

exit = False
i, j = 0, 0
while j + 1 < len(trace):
    while True:
        if j+1 >= len(trace) or trace[j+1]['message'].startswith('. '):
            break
        j += 1

    t_tot = trace[i]['t_delta_ns']
    if t_tot < ARGS.min_t_delta:
        i, j = j + 1, j + 1
        continue

    print('\t'.join([str(k) for k in trace[i].values()]) + ' ns')
    for t in trace[i+1:j+1]:
        if t['t_delta_ns'] / t_tot >= ARGS.min_percentage:
            print('\t'.join([str(v) for v in t.values()]) +
                  ' ns\t{:5.2f}%'.format(t['t_delta_ns'] / t_tot*100))
    print('#' * 21)
    i, j = j + 1, j + 1
