"""
gspread class with utilities for the masses

GspreadHelper class extends gspread functionality with retry methods
provided by tenacity
"""
import gspread
from tenacity import retry, wait_fixed, stop_after_attempt
from oauth2client.service_account import ServiceAccountCredentials
#from tenacity_utils import retry_wrapper

class GspreadHelper():
    """ Helper class for gspread worksheet/sheet objects"""
    MAX_ROW = 1000
    MAX_COL = 26

    def __init__(self, drive_api_creds, workbook_name):
        self.cred_json = drive_api_creds
        creds = self.get_goog_creds()
        self.client = self.__retry_wrapper( \
                      gspread.authorize, creds)
        self.workbook = self.__retry_wrapper( \
                        self.client.open, workbook_name)

        self.current_sheet = None
        self.list_worksheets = self.__retry_wrapper(self.workbook.worksheets)

    def get_goog_creds(self):
        """
        Gets creds for sheets and drive
        """
        scope = ['https://spreadsheets.google.com/feeds',\
                 'https://www.googleapis.com/auth/drive']

        account_creds = ServiceAccountCredentials.from_json_keyfile_name( \
                       self.cred_json, scope)

        return account_creds

    #@property
    #def current_sheet(self):
    #    """ Current Sheet Selcted"""
    #    return self.current_sheet
#
    #@current_sheet.setter
    #def current_sheet(self, sheet_name):
    #    self.current_sheet = self.workbook.worksheet(sheet_name)

    @retry(wait=wait_fixed(0.2), stop=stop_after_attempt(5))
    def __retry_wrapper(self, function, *args, **kwargs): #pylint: disable=R0201
        return function(*args, **kwargs)

    def add_sheet(self, sheet_name):
        if sheet_name in self.list_worksheets:
            raise "ValueError"
        else:
            self.__retry_wrapper(
                self.workbook.add_worksheet, sheet_name, GspreadHelper.MAX_ROW,
                GspreadHelper.MAX_COL
            )

    def remove_sheet(self, arg):
        pass

    def get_worksheets(self):
        return self.list_worksheets

    @retry(wait=wait_fixed(1), stop=stop_after_attempt(5))
    def get_all_records(self, sheet=None, head=1):
        try:
            _records = self.current_sheet.get_all_records(head)
        except Exception as ex:
            print(ex)
        else:
            return _records

    @retry(wait=wait_fixed(1), stop=stop_after_attempt(5))
    def get_all_values(self, sheet=None):
        try:
            _records = self.current_sheet.get_all_values()
        except Exception as ex:
            print(ex)
        else:
            return _records

    def open_sheet(self, sheet_name):
        try:
            sheet = self.__retry_wrapper(self.workbook.worksheet, sheet_name)
            return sheet
        except gspread.v4.exceptions.GSpreadException as exception:
            print("Cannot open worksheet: {}".format(sheet_name))
            print("Error: {}".format(exception))

    @retry(wait=wait_fixed(1), stop=stop_after_attempt(5))
    def update_cell(self, target_row, target_col, value, sheet=None):
        if not sheet:
            self.__retry_wrapper(self.current_sheet.update_cell,
                                 target_row,
                                 target_col,
                                 value)
        else:
            _sheet = self.open_sheet(sheet)
            self.__retry_wrapper(_sheet.update_cell,
                                 target_row,
                                 target_col,
                                 value)

    def copy_worksheet(self, origin_sheet, destination_sheet):
        """Copies origin worksheet to destination using origin row and col count

        Inputs are of class gspread.v4  .models.Worksheet
        destination_sheet should already exist
        """
        max_rows = origin_sheet.row_count
        max_cols = origin_sheet.col_count

        origin_cell_list = self.__retry_wrapper(\
                           origin_sheet.range, 1, 1, max_rows, max_cols)
        self.__retry_wrapper(destination_sheet.update_cells, origin_cell_list)

    def duplicate_worksheet(self, origin_sheet_name, new_sheet_name):
        """Creates new duplicate copy of origin_sheet in workbooks

        Input args are string names of origin and destination sheets
        """

        try:
            _origin_sheet = self.__retry_wrapper( \
                            self.workbook.worksheet, origin_sheet_name \
                            )
            self.__retry_wrapper( \
                self.workbook.add_worksheet, new_sheet_name, \
                _origin_sheet.row_count, _origin_sheet.col_count)
        except gspread.v4.exceptions.GSpreadException as ex:
            print("Cannot create new worksheet: {}".format(origin_sheet_name))
            print("Error: {}".format(ex))

        _new_sheet = self.__retry_wrapper( \
                            self.workbook.worksheet, new_sheet_name \
                     )

        self.copy_worksheet(_origin_sheet, _new_sheet)
