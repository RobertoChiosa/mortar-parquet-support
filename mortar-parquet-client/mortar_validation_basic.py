# Author:       Roberto Chiosa
# Copyright:    Roberto Chiosa, © 2023
# Email:        roberto.chiosa@polito.it
#
# Created:      17/04/23
# Script Name:  mortar_validation_buildingMOTIF.py
# Path:         mortar-parquet-client
#
# Script Description:
#
#
# Notes:


import logging
import os

from brickschema import Graph
from buildingmotif import BuildingMOTIF
from rdflib import Namespace

if __name__ == "__main__":

    root = logging.getLogger()
    list(map(root.removeHandler, root.handlers))
    list(map(root.removeFilter, root.filters))

    # define base path
    raw_data_path = os.path.join("graphs")
    clean_data_path = os.path.join("graphs_clean")

    bm = BuildingMOTIF("sqlite://")
    BLDG = Namespace('urn:bldg/')

    # define logger pro
    logger = logging.getLogger(__name__)
    # list all files ttl in folder and loop for validation

    for file in os.listdir(clean_data_path):

        g = Graph(load_brick=True)
        g.load_file(os.path.join(raw_data_path, file))
        valid, _, report = g.validate()
        print(f"Graph <{file}> is valid? {valid}")
        if not valid:
            print("-" * 79)
            print(report)
            print("-" * 79)
