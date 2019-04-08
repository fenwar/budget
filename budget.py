#!/usr/bin/env python3

import argparse
import datetime
import sys

from dateutil.relativedelta import relativedelta

from service import connect_to_api
from payment import PaymentRow
from recurrence import RecurringPayment

SPREADSHEET_ID = "1iyPkOwg_sQcxYIFruC7kjWiq4FLuD6SkHZmxR4KDR6Y"
TEMPLATE_RANGE = "Recurring Payments!B5:G"
BLANK_SHEET = "Blank Month"

DATE_PARSE_FORMAT="%Y-%m-%d"
DATE_HUMAN_FORMAT="YYYY-MM-DD"

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--create",
        type=date_argument,
        metavar=DATE_HUMAN_FORMAT,
        help="""Create a budget sheet with recurring payments for 1 month
                starting from %(metavar)s.""")
    raw_args = ap.parse_args()
    return ap.parse_args()


def date_argument(arg):
    try:
        return datetime.datetime.strptime(arg, DATE_PARSE_FORMAT).date()
    except ValueError:
        raise argparse.ArgumentTypeError(
                """Please enter a date in the format {0} (couldn't parse {1}).
                """.format(DATE_HUMAN_FORMAT, arg))


def main():
    sheets_api = connect_to_api()
    args = parse_args()
    budget = BudgetTemplate(sheets_api)

    if args.create:
        payments = budget.create_new_month(args.create)
        
        for payment in payments:
            print(payment)

    else:
        # work out the budget totals for an entire calendar year:
        payments = budget.generate_payments(
            datetime.date(2018, 11, 1),
            datetime.date(2019, 11, 30),
        )
        total = 0
        for payment in payments:
            print(payment)
            total += payment.amount

        print("Total balance is {}.".format(total))


class BudgetTemplate():
    def __init__(self, sheets_api):
        """
        Load the recurring payments template
        """
        self.api = sheets_api
        template_data = self.api.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=TEMPLATE_RANGE,
                valueRenderOption="FORMULA").execute()
        self.recurring_items = []
        for row in template_data.get("values", []):
            if row and row[0]:
                self.recurring_items.append(RecurringPayment(*row))
        self.blank_sheet_id = self.get_blank_month_sheet_id()

    def generate_payments(self, start_date, end_date):
        """
        Generate the list of payments between the two dates
        """
        payments = []
        for rec_item in self.recurring_items:
            for payment_date in rec_item.get_payments_for_range(start_date, end_date):
                payments.append(
                    PaymentRow(payment_date, rec_item.description, rec_item.amount))
        payments.sort(key=lambda x:x.payment_date)
        return payments

    def get_blank_month_sheet_id(self):
        """
        Return the ID of the sheet to be copied to start off a blank month.

        While I could hard-code this I'd prefer to use the name; there might be
        a simpler way to look up a sheet by name.
        """
        sheet = self.api.spreadsheets().getByDataFilter(
            spreadsheetId=SPREADSHEET_ID,
            body={
                "dataFilters": [
                    {
                        "a1Range": BLANK_SHEET,
                    }
                ],
                "includeGridData": False,
            }).execute()
        return sheet.get("sheets")[0].get("properties").get("sheetId")

    def create_new_month(self, start_date):
        """
        Create a sheet for the month starting from start_date and populate it
        with all the payments.
        """
        sheet_title = start_date.strftime("%B %Y")
        end_date = start_date + relativedelta(months=1, days=-1)
        payments = self.generate_payments(start_date, end_date)

        data = {"requests": [
            {"duplicateSheet": {
                "sourceSheetId": self.blank_sheet_id,
                "insertSheetIndex": 0,
                "newSheetName": sheet_title,
            }},
        ]}
        result = self.api.spreadsheets().batchUpdate(
                spreadsheetId=SPREADSHEET_ID, body=data).execute()

        new_month_sheet_id = result["replies"][0]["duplicateSheet"]["properties"]["sheetId"]

        # change the colour of the sheet
        data = {"requests": [
            {"updateSheetProperties": {
                "properties": {
                    "sheetId": new_month_sheet_id,
                    "tabColor": {
                        "red": 0.2,
                        "blue": 0.1,
                        "green": 0.8,
                    },
                },
                "fields": "tabColor",
            }},
        ]}
        result = self.api.spreadsheets().batchUpdate(
                spreadsheetId=SPREADSHEET_ID, body=data).execute()

        # append the payment data to the sheet:
        result = self.api.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID,
                range="{}!A5:E5".format(sheet_title),
                valueInputOption="USER_ENTERED",
                body={"values": [payment.as_row_values() for payment in payments]}).execute()

        # copy the running total formula to the whole column:


        return payments

if __name__ == "__main__":
    sys.exit(main())
