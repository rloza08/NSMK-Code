#!/usr/bin/env python3
"""Used only to keep pylint quiet"""
import utils.auto_utils as auto_utils

from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput

with PyCallGraph(output=GraphvizOutput()):
    auto_utils.create_store_data_dir()