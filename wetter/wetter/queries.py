"""Queries for the selection of measurements on different criteria.

These functions are executing different queries on measurement datasets.
Most of them share the same parameter space with `df` for the DataFrame used
as `pandas` and a `date` object used for context. Some functions might define
additional parameters for context. All of these functions share the same
output type. This allows the chaining of queries.
"""

from datetime import timedelta


def latest_datapoint(df, date):
    """Retrieve the latest measurement not exceding a certain date.

    This function returns the latest measurement, which is still
    before a certain date. It will return a DataFrame which consists of
    a single row. This way it is easier

    :param df: Database with all measurements
    :type df: pandas.DataFrame
    :param date: Upper limit for search of latest measurement
    :type date: datetime.datetime [UTC]
    :return: The latest measurement
    :rtype: pandas.DataFrame
    """
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
    :type date: datetime.datetime [UTC]
    :return: The latest measurement
    :rtype: pandas.DataFrame
    """
    threshold = date - timedelta(days=7)
    result = df[(df.index >= threshold) & (df.index < date)]
    return result


def last_month(df, date):
    """Retrieve all measurements of last month.

    :param df: Database with all measurements
    :type df: pandas.DataFrame
    :param date: Date used as context to define last month
    :type date: datetime.datetime [UTC]
    :return: The latest measurement
    :rtype: pandas.DataFrame
    """
    year, month = (date.year, date.month - 1) if date.month != 1 else (date.year - 1, 12)
    result = df[(df.index.year == year) & (df.index.month == month)]
    return result


def last_year(df, date):
    """Retrieve all measurements of last year.

    :param df: Database with all measurements
    :type df: pandas.DataFrame
    :param date: Date used as context to define last year
    :type date: datetime.datetime [UTC]
    :return: The latest measurement
    :rtype: pandas.DataFrame
    """
    result = df[df.index.year == date.year - 1]
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
    :type date: datetime.datetime [UTC]
    :return: The latest measurement
    :rtype: pandas.DataFrame
    """
    year = date.year if date.month > month else date.year - 1
    result = df[(df.index.year == year) & (df.index.month == month)]
    return result
