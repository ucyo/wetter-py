"""Queries for the selection of measurements on different criteria.

These functions are executing different queries on measurement datasets.
Most of them share the same parameter space with `df` for the DataFrame used
as `pandas` and a `date` object used for context. Some functions might define
additional parameters for context. All of these functions share the same
output type. This allows the chaining of queries.
"""
from datetime import timedelta
from datetime import datetime as dt


def latest_datapoint(df, date):
    """Retrieve the latest measurement not exceding a certain date.

    This function returns the latest measurement, which is still
    before a certain date. It will return a DataFrame which consists of
    a single row. This way it is easier

    :param df: Database with all measurements
    :type df: pandas.DataFrame
    :param date: Upper limit for search of latest measurement
    :type date: datetime.datetime w/ time zone information
    :return: The latest measurement
    :rtype: pandas.DataFrame
    """
    assert date.tzinfo is not None
    df = df[df.index < date]
    result = df[df.index == df.index.max()]
    return result


def last_week(df, date):
    """Retrieve all measurements within a week before a certain date (excluding).

    Returns the measurements of one week earlier than a specific date.
    The date is not included in the query.

    :param df: Database with all measurements
    :type df: pandas.DataFrame
    :param date: Upper limit for search of latest measurement
    :type date: datetime.datetime w/ time zone information
    :return: The latest measurement
    :rtype: pandas.DataFrame
    """
    assert date.tzinfo is not None
    threshold = date - timedelta(days=7)
    result = _windowed_selection(df, threshold, date)
    return result


def last_month(df, date):
    """Retrieve all measurements of last month.

    :param df: Database with all measurements
    :type df: pandas.DataFrame
    :param date: Date used as context to define last month
    :type date: datetime.datetime w/ time zone information
    :return: The latest measurement
    :rtype: pandas.DataFrame
    """
    assert date.tzinfo is not None
    if date.month != 1:
        year, month = (date.year, date.month - 1)
    else:
        year, month = (date.year - 1, 12)
    start = dt(year=year, month=month, day=1, tzinfo=date.tzinfo)
    days_of_month = 33 - (start + timedelta(days=33)).day
    end = start.replace(month=start.month, day=days_of_month, hour=23, minut=59, second=59)
    result = _windowed_selection(df, start, end)
    return result


# Pandas allows for easy selection of month/year by using
# the following syntax: `result = df[df.index.year == date.year - 1]`
# It is very short and nice looking. But(!) it does not consider
# time zone. The following implementation actually considers
# timezones and selects data accordingly.
def last_year(df, date):
    """Retrieve all measurements of last year.

    :param df: Database with all measurements
    :type df: pandas.DataFrame
    :param date: Date used as context to define last year
    :type date: datetime.datetime w/ time zone information
    :return: The latest measurement
    :rtype: pandas.DataFrame
    """
    assert date.tzinfo is not None
    start = dt(year=date.year - 1, month=1, day=1, tzinfo=date.tzinfo)
    end = start.replace(year=start.year + 1) - timedelta(seconds=1)
    result = _windowed_selection(df, start, end)
    return result


def specific_month(df, date, month):
    """Retrieve all measurements of a specific month.

    The month will be calculated relative to the given date. Is the month
    higher than the one defined in the date element, than the measurements
    from last year will be returned. If the month already occurred this year,
    then the data from the current year is returned.

    :param df: Database with all measurements
    :type df: pandas.DataFrame
    :param date: Date used as context to define if month already past this year
    :type date: datetime.datetime w/ time zone information
    :return: The latest measurement
    :rtype: pandas.DataFrame
    """
    assert date.tzinfo is not None
    year = date.year if date.month > month else date.year - 1
    start = dt(year=year, month=month, day=1, tzinfo=date.tzinfo)
    days_of_month = 33 - (start + timedelta(days=33)).day
    end = start.replace(month=start.month, day=days_of_month, hour=23, minut=59, second=59)
    result = _windowed_selection(df, start, end)
    return result


def _windowed_selection(df, start, end):
    """Select a time period in database considering time zones.

    This function takes the timezone into consideration when selecting data.
    Both borders are included in the data selection.

    :param df: Database with all measurements
    :type df: pandas.DataFrame
    :param start: Start date of time period
    :type start: datetime.datetime w/ time zone information
    :param end: End date of time period
    :type end: datetime.datetime w/ time zone information
    """
    return df[(df.index <= end) & (df.index >= start)]
