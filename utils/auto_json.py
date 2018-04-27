#!/usr/bin/env python3
from utils._json import Json
from utils._csv import transform_to_csv

def reader(fname, configDir="data"):
    """Reads json file"""
    data = Json.reader(fname, configDir)
    return data

def writer(fname, data, path="data", header=None, logPath=False):
    if data is None:
        return
    Json.writer(fname, data, path=path, absolute_path=None, logPath=logPath)
    transform_to_csv(fname, path=path, header=header)

def make_pretty(my_json):
    return Json.make_pretty(my_json)

if __name__ == '__main__':
    csvfile = 'firewall-rules.csv'
    fname = "json-csv-conversion"

