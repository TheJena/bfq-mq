#!/usr/bin/env python3

import argparse

try:
    import tabulate
except ModuleNotFoundError as e:
    if str(e) == "No module named 'tabulate'":
        print('Please install python3-tabulate')
        exit(1)

def parse_duration(record):
    rec = record.split()
    offset = int(bool(rec[1] == '+'))
    return {'location': ''.join(rec[:2+offset]),
            'message': ' '.join(rec[2+offset:-3]),
            't_delta_ns': int(rec[-2:-1][0])}

def parse_mean_duration(record):
    rec = record.split()
    offset = int(bool(rec[1] == '+'))
    return {'location': ''.join(rec[:2+offset]),
            'message': ' '.join(rec[2+offset:-3]),
            't_means_ns': int(rec[-2:-1][0])}

def parse_total_duration(record):
    rec = record.split()
    offset = int(bool(rec[1] == '+'))
    return {'location': ''.join(rec[:2+offset]),
            'message': ' '.join(rec[2+offset:-5]),
            't_tot_us': round(float(rec[-4:-3][0]) / 10**3, 3),
            'calls': int(rec[-1])}

parser = argparse.ArgumentParser()
parser.add_argument(help='/sys/kernel/debug/tracing/trace',
                    metavar='trace',
                    type=open,
                    dest='input_file')
ARGS = parser.parse_args()

trace = {'t_delta': [], 't_mean': [], 't_tot': []}
for line in ARGS.input_file.readlines():
    if 'block/' not in line:
        continue
    if not line.startswith('block/'):
        line = 'block/' + line.split('block/')[1]

    if 't_delta' in line:
        trace['t_delta'].append(parse_duration(line))
    elif 't_mean' in line:
        trace['t_mean'].append(parse_mean_duration(line))
    elif 't_tot' in line:
        trace['t_tot'].append(parse_total_duration(line))
    else:
        print('WARNING unrecognized line "{}"'.format(line))

t_tot_table = {loc: sorted((rec for rec in trace['t_tot']
                            if rec['location'] == loc),
                           key=lambda d: d['t_tot_us'] + d['calls'],
                           reverse=True)[0]
               for loc in set(rec['location'] for rec in trace['t_tot'])}

print(tabulate.tabulate(sorted(t_tot_table.values(),
                               key=lambda d: d['t_tot_us'],
                               reverse=True),
                        headers="keys",
                        tablefmt='psql'))
print('t_tot sum: {:.3f} us'.format(sum(rec["t_tot_us"]
                                        for rec in t_tot_table.values())))
