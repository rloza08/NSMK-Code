#!/usr/bin/env python3
from utils.low_json import Json
from utils.low_csv import transform_to_csv
import utils.low_csv as csv

def reader(fname, configDir="data"):
    """Reads json file"""
    data = Json.reader(fname, configDir)
    return data

def writer(fname, data, path="data", header=None):
    if data is None:
        return
    Json.writer(fname, data, path=path)
    transform_to_csv(fname, path=path, header=header)

def convert_to_json(fname, path, absolute_path):
    obj = csv.Csv()
    obj.to_json(fname, path, absolute_path)

def convert_to_json_and_validate(fname, input_path, output_dir):
    obj = csv.Csv()
    obj.to_json_and_validate(fname, input_path, output_dir)

def convert_to_csv_and_validate(fname, input_path, output_dir):
    obj = csv.Csv()
    obj.to_csv_and_validate(fname, input_path, output_dir)


if __name__ == '__main__':
    fname = 'test'
    convert_to_json(fname)
