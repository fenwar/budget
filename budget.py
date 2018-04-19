#!/usr/bin/env python3

from datetime import date

from service import connect_to_api
from recurrence import RecurringPayment

SPREADSHEET_ID = "1iyPkOwg_sQcxYIFruC7kjWiq4FLuD6SkHZmxR4KDR6Y"
TEMPLATE_RANGE = "Template!B5:G"

if __name__ == "__main__":
    sheets_api = connect_to_api()
    template_data = sheets_api.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=TEMPLATE_RANGE,
            valueRenderOption="FORMULA").execute()

    START_DATE = date(2018, 4, 7)
    END_DATE = date(2018, 5, 6)

    payments = []

    for row in template_data.get("values", []):
        if row and row[0]:
            print(row)
            rec_item = RecurringPayment(*row)
            payments.extend(rec_item.get_payments_for_range(START_DATE, END_DATE))

    print(payments)
