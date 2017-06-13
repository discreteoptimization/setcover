#!/usr/bin/env python
# encoding: utf-8
from collections import namedtuple
import os
import re
import sys

Set = namedtuple("Set", ['index', 'cost', 'items'])
Task = namedtuple('Task', ['item_count', 'set_count', 'sets'])

DATA_ROOT = os.path.realpath(os.path.join(__file__, '../../data'))


def parse_input(input_data):
    lines = input_data.split('\n')

    parts = lines[0].split()
    item_count = int(parts[0])
    set_count = int(parts[1])

    sets = []
    for idx, line in enumerate(lines[1:set_count+1]):
        parts = line.split()
        sets.append(Set(idx, float(parts[0]), map(int, parts[1:])))

    return Task(item_count, set_count, sets)


def read_input(filename):
    path =  os.path.join(DATA_ROOT, filename)
    with open(path) as f:
        return parse_input(f.read())


def get_size(filename):
    num = re.search(r'\d+', filename)
    if num is None:
        return None
    else:
        return int(num.group(0))


def list_files(min_size=0, max_size=sys.maxint):
    files = sorted((get_size(fn), fn) for fn in os.listdir(DATA_ROOT))
    return [fn for f_size, fn in files
            if fn is not None and min_size <= f_size <=max_size]
