#!/usr/bin/env python3

"""
Logging utilities.
"""

TRACE = 100
INFO = 200
WARN = 300
ERROR = 400


import time
import datetime
from conf import constants
import os
from conf import config


LEVEL = config.LOGGER_LEVEL


ERROR_OUTPUT = os.path.join(config.LOGS_DIR, constants.ERROR_LOG)
INFO_OUTPUT = os.path.join(config.LOGS_DIR, constants.INFO_LOG)
EXCHANGE_OUTPUT = os.path.join(config.LOGS_DIR, constants.EXCHANGE_LOG)
TRADES_OUTPUT = os.path.join(config.LOGS_DIR, constants.TRADES_LOG)

def get_timestamp():
    return datetime.datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

def timestamp_string(s):
    ts = get_timestamp()
    return f'{ts} {s}'   

def trace(s='\n'):
    if LEVEL >= TRACE:
        print(s)

def info(s):
    tss = timestamp_string(s)
    with open(INFO_OUTPUT, 'a') as out:        
        out.write(f'INFO: {tss}\n')
    if LEVEL >= INFO:
        print(tss)
        

def exchange_trace(s):
    tss = timestamp_string(s)
    with open(EXCHANGE_OUTPUT, 'a') as out:        
        out.write(f'EXCHANGE TRACE: {tss}\n')
    if LEVEL >= INFO:
        print(tss)


def warn(s):
    tss = timestamp_string(s)
    with open(ERROR_OUTPUT, 'a') as out:
        out.write(f'WARNING: {tss}\n')
    if LEVEL >= WARN:
        print(tss)


def error(s):
    tss = timestamp_string(s)
    with open(ERROR_OUTPUT, 'a') as out:
        out.write(f'ERROR: {tss}\n')
    if LEVEL >= ERROR:
        print(tss)


def trade(s):
    tss = timestamp_string(s)
    with open(TRADES_OUTPUT, 'a') as out:
        out.write(f'{tss}\n')
    if LEVEL >= INFO:
        print(tss)


