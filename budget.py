#!/usr/bin/env python3

from service import connect_to_api

SPREADSHEET_ID = "1eIwfJBacEsLZZ27CEqD819cNxsXz_ooxhpzGBs7KFL8"
TEMPLATE_RANGE = "Month Template 2017"

if __name__ == "__main__":
    sheets_api = connect_to_api()

    rows = sheets_api.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=TEMPLATE_RANGE).execute()

    print(rows)
