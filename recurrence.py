from datetime import date
from dateutil.rrule import rrule, MONTHLY, WEEKLY
from decimal import Decimal

from functools import partial

class RecurringPayment(object):

    def __init__(self, recurrence, description,
                 amount_in=None, amount_out=None,
                 start_date=date.min, end_date=date.max):
        if not amount_in:
            amount_in = "0.00"
        if not amount_out:
            amount_out = "0.00"
        self.description = description

        self.amount = Decimal(amount_in) - Decimal(amount_out)
        self.start_date = start_date
        self.end_date = end_date

        if recurrence == "w":
            self.part_rule = partial(rrule, freq=WEEKLY)
        elif recurrence == "2w":
            self.part_rule = partial(rrule, freq=WEEKLY, interval=2)
        elif recurrence == "4w":
            self.part_rule = partial(rrule, freq=WEEKLY, interval=4)
        else:
            # An integer value on its own just means monthly on this date
            monthday = int(recurrence)
            self.part_rule = partial(rrule, freq=MONTHLY, bymonthday=monthday)

    def get_payments_for_range(self, range_start, range_end):
        return list(self.part_rule(
                dtstart=max(range_start, self.start_date),
                until=min(range_end, self.end_date)))
