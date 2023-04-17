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

import brickschema
from buildingmotif import BuildingMOTIF
from buildingmotif.dataclasses import Model, Library
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
    for file in os.listdir(raw_data_path):

        # load the graph
        model = Model.create(BLDG, description="This is a test model for a simple building")
        # parse mortar building graph
        model.graph.parse(os.path.join(raw_data_path, file), format="ttl")
        # add brick ontology
        brick = Library.load(ontology_graph="Brick-subset.ttl")
        # validate the ttl with brick subset
        validation_result = model.validate([brick.get_shape_collection()])
        # print validation result
        print(f"Model <{file}> is valid? {validation_result.valid}")
        # if not valid print the validation results
        if not validation_result.valid:
            print("-" * 79)  # just a separator for better error display
            print(validation_result.report_string)
            print("-" * 79)  # just a separator for better error display
            print("Model is invalid for these reasons:")
            for diff in validation_result.diffset:
                print(f" - {diff.reason()}")
        else:

            # create new instance of graph
            g = brickschema.Graph()
            # adds the system metadata schema to the graph
            g.parse(os.path.join(raw_data_path, file), format="ttl")
            # save serialized and tidy graph
            g.serialize(os.path.join(clean_data_path, file), format="ttl")
