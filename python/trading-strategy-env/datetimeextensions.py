import datetime


class DateTimeExtensions:
    @staticmethod
    def difference_in_years(date1: datetime.date, date2: datetime.date):
        return (date2-date1).days/365.0

    @staticmethod
    def difference_in_months(date1: datetime.date, date2: datetime.date):
        return DateTimeExtensions.difference_in_years(date1, date2) * 12.0
