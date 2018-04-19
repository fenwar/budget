
class PaymentRow(object):
    """
    represents an actual payment on a given date.
    """
    def __init__(self, payment_date, description, amount):
        self.payment_date = payment_date
        self.description = description
        self.amount = amount

    def as_row_values(self):
        """
        Provide the details in the format of the monthly sheet, with these columns:

        Expected date
        Bank date
        Description
        Amount in
        Amount out
        """
        row = [self.payment_date.strftime("%d/%m/%Y"), '', self.description, '', '']
        if self.amount > 0:
            row[3] = str(self.amount)
        else:
            row[4] = str(-self.amount)
        return row
