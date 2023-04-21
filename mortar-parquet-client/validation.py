# Author:       Roberto Chiosa
# Copyright:    Roberto Chiosa, © 2023
# Email:        roberto.chiosa@polito.it
#
# Created:      21/04/23
# Script Name:  validation.py
# Path:         mortar-parquet-client
#
# Script Description:
#
#
# Notes:

import logging
import os

from brickschema import Graph
from buildingmotif.dataclasses import Model, Library
from rdflib import Namespace


class BasicValidationInterface:
    """
    This class is used to validate a graph using the Brick basic validation as described here:
    https://github.com/gtfierro/shapes/blob/main/verify.py
    """

    def __init__(self, graph_path: str, nightly: bool = False):
        self.graph_path = graph_path
        if nightly:
            self.graph = Graph(load_brick_nightly=True)
        else:
            self.graph = Graph(load_brick=True)

    def validate(self):
        self.graph.load_file(self.graph_path)
        valid, _, report = self.graph.validate()
        print(f"Graph <{self.graph_path}> is valid? {valid}")
        if not valid:
            print("-" * 79)
            print(report)
            print("-" * 79)


class BuildingMotifValidationInterface:

    def __init__(self, graph_path: str):
        # Define graph path
        self.graph_path = graph_path

    def validate(self):
        # create the namespace for the building
        bldg = Namespace('urn:bldg/')
        # create the building model
        model = Model.create(bldg, description="This is a test model for a simple building")
        # load test case model
        model.graph.parse(self.graph_path, format="ttl")
        print(f"Model length {len(model.graph.serialize())}")
        # load libraries included with the python package
        constraints = Library.load(ontology_graph="../../buildingmotif/libraries/constraints/constraints.ttl")
        # load libraries excluded from the python package (available from the repository)
        brick = Library.load(ontology_graph="Brick-subset.ttl")
        print(f"Model + brick length {len(model.graph.serialize())}")
        # load manifest into BuildingMOTIF as its own library!
        # manifest = Library.load(ontology_graph=self.manifest_path)

        # gather shape collections into a list for ease of use
        shape_collections = [
            brick.get_shape_collection(),
            constraints.get_shape_collection(),
            # manifest.get_shape_collection(),
        ]

        # pass a list of shape collections to .validate()
        validation_result = model.validate(shape_collections)
        # print validation result
        print(f"Model <{self.graph_path}> is valid? {validation_result.valid}")
        # if not valid print the validation results
        if not validation_result.valid:
            print("-" * 79)  # just a separator for better error display
            print(validation_result.report_string)
            print("-" * 79)  # just a separator for better error display
            print("Model is invalid for these reasons:")
            for diff in validation_result.diffset:
                print(f" - {diff.reason()}")


if __name__ == "__main__":
    # remove logger from building motif
    root = logging.getLogger()
    list(map(root.removeHandler, root.handlers))
    list(map(root.removeFilter, root.filters))

    for file in os.listdir('graphs_clean'):
        # get the relative path of the file
        path = os.path.join('graphs_clean', file)
        # validate using basic brick validation
        bv = BasicValidationInterface(graph_path=path, nightly=True)
        bv.validate()
        # validate using building motif
        # bmv = BuildingMotifValidationInterface(graph_path=path)
        # bmv.validate()
