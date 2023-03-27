import argparse
import glob
import os

import rdflib

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("graph_dir", help="Folder containing .ttl files", type=str, default="graphs")
    parser.add_argument("db_dir", help="Destination of on-disk database", type=str, default="graph.db")
    args = parser.parse_args()

    store = rdflib.Dataset(store="OxSled")
    store.default_union = True  # queries default to the union of all graphs
    store.open(args.db_dir)
    ttl_files = glob.glob(os.path.join(args.graph_dir, "*.ttl"))
    for ttl_file in ttl_files:
        graph_name = os.path.splitext(os.path.basename(ttl_file))[0]
        graph_name = f"urn:{graph_name}#"
        graph = store.graph(graph_name)
        print(f"Loading {ttl_file} => ", end='', flush=True)
        graph.parse(ttl_file, format="ttl")
        graph.parse("https://github.com/BrickSchema/Brick/releases/download/nightly/Brick.ttl", format="ttl")
        print(f"Done as {graph_name}")
