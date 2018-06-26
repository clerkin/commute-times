#!/usr/bin/env python3

"""
Intro to this Program

Program Flow:
- Python script is called by Cron Job on BBB at specified intervals
- Script starts by checking current time, establishing cell indexes
- Script then submits Google Directions request to find time in traffic
- Script then writes travel time into cell
- Script then exits

V2 of script will be capable of:
- Performing return trip commute times
- Error checking for internet connection
- Error checking for kick off at wrong time of day
- Log file to document errors encountered in execution

"""

import logging
import calendar
from datetime import datetime
from GspreadHelper import GspreadHelper
import google_map_helpers as gmh
from config import get_conf
import pdb

def get_time_and_day():
    """
    Returns current time and day
    """
    current_datetime = datetime.now()
    return current_datetime.strftime('%H:%M'), current_datetime.weekday()

def main():
    """
    The real meat henny
    """
    drive_api_creds = get_conf("drive_api_creds")
    maps_api_key = get_conf("maps_api_key")
    home = get_conf("home").replace(' ', '+')
    work = get_conf("work").replace(' ', '+')

    book = GspreadHelper(drive_api_creds, "commute_times")

    time, day_of_week = get_time_and_day()
    week_sheet = 'Week {}'.format(str(datetime.now().isocalendar()[1]))

    # Get time in traffic from A to B in minutes
    travel_time = gmh.time_in_traffic_sec(home, work, maps_api_key)
    travel_time = int(travel_time/60)

    # See if sheet already exists, of not make it
    worksheet_list = []
    for sheet in book.list_worksheets:
        worksheet_list.append(sheet.title)

    if week_sheet in worksheet_list:
        book.current_sheet = book.open_sheet(week_sheet)
    else:
        book.duplicate_worksheet("TEMPLATE", week_sheet)
        book.current_sheet = book.open_sheet(week_sheet)

    # pull all values in sheet to determine row and index (minimize requests)
    #sheet_values = sheet.get_all_records(head=1)
    sheet_values = book.get_all_records()
    sheet_vals = book.get_all_values()
    #print(list(l for l in sheet_vals))

    # generate lists of row and col indexes to find target cell coordinates
    row_indices = [d['Time'] for d in sheet_values]
    col_indices = sheet_vals[0]

    # Now find the target cell from our current time and day
    target_row = row_indices.index(time) + 2
    target_col = col_indices.index(calendar.day_name[day_of_week]) + 1
    #pdb.set_trace()
    # Get time in traffic from A to B
    #book.current_sheet.update_cell(target_row, target_col, travel_time)
    book.update_cell(target_row, target_col, travel_time)

if __name__ == '__main__':
    main()
