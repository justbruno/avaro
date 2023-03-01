#!/usr/bin/env python3

"""
Helpers for I/O.
"""

import datetime

def load_conf(filename):
    return update_conf({}, filename)


def update_conf(configuration, filename):
    with open(filename, 'r') as f:
        for l in f:
            r = l.split('#')[0]
            s = r.replace(' ', '').strip('\n').split('=')
            configuration[s[0]] = eval(s[1])
    return configuration


def save_conf(configuration, filename):
    with open(filename, 'w') as f:
        for k in configuration:
            f.write(f'{k}={configuration[k]}\n')

def timestamp_to_epoch(s):
    return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S').timestamp()
