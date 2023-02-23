#!/usr/bin/env python3

"""
Helpers for I/O.
"""

def load_conf(filename):
    configuration = {}
    with open(filename, 'r') as f:
        for l in f:
            r = l.split('#')[0]
            s = r.replace(' ', '').strip('\n').split('=')
            configuration[s[0]] = eval(s[1])
    return configuration


def update_conf(configuration, filename):
    with open(filename, 'r') as f:
        for l in f:
            r = l.split('#')[0]
            s = r.replace(' ', '').strip('\n').split('=')
            configuration[s[0]] = eval(s[1])
    return configuration
