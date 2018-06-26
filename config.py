"""
Utilities to get configuration from json file and ENV variables
"""
from os import environ as ENV
import json

JSON_PATH = './config.json'

def read_json(file_path):
    # Reads from JSON
    try:
        with open(file_path) as file_pointer:
            data = json.load(file_pointer)
        return data
    except IOError:
        return {}

def get_from_json(var_name):
    # Gets from JSON
    try:
        return read_json(JSON_PATH)[var_name]
    except KeyError:
        return None

def get_conf(var_name):
    """
    this helper looks in VT_SYSTEMD_JSON_PATH
    then looks in environment variables
    and returns the configuration
    """
    return get_from_json(var_name) or ENV.get(var_name, None)
