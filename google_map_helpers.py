"""
goog map utilities for the masses
"""
import urllib.request
import json
import logging
from oauth2client.service_account import ServiceAccountCredentials


def time_in_traffic_sec(origin, destination, api_key):
    """
    Returns time in traffic from origin to destination
    """
    endpoint = 'https://maps.googleapis.com/maps/api/directions/json?'
    departure_time = 'now'

    nav_req = 'origin={}&destination={}&departure_time={}&key={}'.format(\
               origin, destination, departure_time, api_key)
    req = endpoint + nav_req
    #response = urllib.request.urlopen(req)

    try:
        response = urllib.request.urlopen(req)
    except urllib.error.HTTPError as ex:
        logging.error('HTTPError = ' + str(ex.code))
    except urllib.error.URLError as ex:
        logging.error('URLError = ' + str(ex.reason))
    directions = json.loads(response.read().decode())
    routes = directions['routes']
    time_in_traffic = routes[0]['legs'][0]['duration_in_traffic']['value']
    return time_in_traffic

def get_goog_creds(api_key_json):
    """
    Gets creds for sheets and drive
    """
    scope = ['https://spreadsheets.google.com/feeds',\
             'https://www.googleapis.com/auth/drive']
    return ServiceAccountCredentials.from_json_keyfile_name(api_key_json, scope)
