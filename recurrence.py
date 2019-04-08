from datetime import date
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, rruleset, DAILY, WEEKLY, MONTHLY, YEARLY
from decimal import Decimal

from functools import partial

SERIAL_BASE = date(1899, 12, 30)

class RecurringPayment(object):

    def __init__(self, recurrence, description,
                 amount_in=None, amount_out=None,
                 start_date=None, end_date=None):
        self.description = description

        if not amount_in:
            amount_in = "0.00"
        if not amount_out:
            amount_out = "0.00"
        self.amount = (Decimal(amount_in) - Decimal(amount_out)).quantize(Decimal("0.00"))

        if start_date:
            self.start_date = SERIAL_BASE + relativedelta(days=start_date)
        else:
            self.start_date = None
        if end_date:
            self.end_date = SERIAL_BASE + relativedelta(days=end_date)
        else:
            self.end_date = None

        if str(recurrence).endswith("w"):
            week_count = recurrence.rstrip("w")
            if week_count:
                week_count = int(week_count)
            else:
                week_count = 1
            self.part_rule = partial(rrule, freq=WEEKLY, interval=week_count)
        elif recurrence == "y":
            self.part_rule = partial(rrule, freq=YEARLY)
        else:
            # An integer value on its own just means monthly on this date
            monthday = int(recurrence)
            self.part_rule = partial(rrule, freq=MONTHLY, bymonthday=monthday)

    def get_payments_for_range(self, range_start, range_end):
        payments = rruleset()

        if self.start_date:
            recurrence_start = self.start_date
        else:
            recurrence_start = range_start

        if self.end_date:
            recurrence_end = self.end_date
        else:
            recurrence_end = range_end

        payments.exrule(rrule(freq=DAILY, dtstart=min(range_start, recurrence_start), until=range_start - relativedelta(days=1)))
        payments.exrule(rrule(freq=DAILY, dtstart=range_end + relativedelta(days=1)))
        payments.rrule(self.part_rule(
                dtstart=recurrence_start,
                until=recurrence_end))

        return list(payments)
