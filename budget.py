#!/usr/bin/env python3

from datetime import date

from service import connect_to_api
from recurrence import RecurringPayment

SPREADSHEET_ID = "1iyPkOwg_sQcxYIFruC7kjWiq4FLuD6SkHZmxR4KDR6Y"
TEMPLATE_RANGE = "Template!B5:G"

class BudgetTemplate():
    def __init__(self, sheets_api):
        """
        Load the recurring payments template
        """
        self.api = sheets_api
        template_data = sheets_api.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=TEMPLATE_RANGE,
                valueRenderOption="FORMULA").execute()
        self.recurring_items = []
        for row in template_data.get("values", []):
            if row and row[0]:
                self.recurring_items.append(RecurringPayment(*row))

    def generate_payments(self, start_date, end_date):
        """
        Generate the list of payments between the two dates
        """
        payments = []
        for rec_item in self.recurring_items:
            for payment_date in rec_item.get_payments_for_range(start_date, end_date):
                payments.append((payment_date, rec_item.description, rec_item.amount))
        payments.sort(key=lambda x:x[0])
        return payments

if __name__ == "__main__":
    sheets_api = connect_to_api()

    budget = BudgetTemplate(sheets_api)

    payments = budget.generate_payments(date(2018, 4, 7), date(2018, 6, 6))

    for payment in payments:
        print(payment)
