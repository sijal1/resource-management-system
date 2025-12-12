from datetime import datetime, timedelta
import holidays

INDIA_HOLIDAYS = holidays.country_holidays("IN")


def calculate_working_days(start_date, end_date):
    """
    start_date, end_date are 'YYYY-MM-DD'
    """

    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()

    if end < start:
        return 0

    wd = 0
    curr = start

    while curr <= end:
        if curr.weekday() < 5 and curr not in INDIA_HOLIDAYS:
            wd += 1
        curr += timedelta(days=1)

    return wd



