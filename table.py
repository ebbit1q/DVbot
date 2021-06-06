"""copied tables and hardcoded values"""
import json
import os


def _get_tables():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(this_dir, "table.json")
    with open(json_file) as fp:
        return json.load(fp)


_tables = _get_tables()
DV = _tables["DV"]
MODIFIERS = _tables["MODIFIERS"]
