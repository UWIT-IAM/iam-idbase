import pytz
from django.utils.timezone import now, localtime
from django.utils.dateparse import parse_datetime


def localized_datetime_string_now():
    """
    Return an ISO-formatted datetime string in the local timezone, which comes from
    settings.TIME_ZONE.
    """
    return localtime(now()).replace(microsecond=0).isoformat()


def datetime_diff_seconds(older_time, newer_time=None):
    """
    Return the seconds elapsed between older_time and newer_time.
    If newer_time is unset, return the seconds elapsed between older_time and now.
    older_time and newer_time are expected to be ISO-formatted datetime strings.
    """
    older_datetime = parse_datetime(older_time)
    if not older_datetime.tzinfo:
        # if no timezone set (naive datetime) we'll assume it to be UTC.
        older_datetime = pytz.UTC.localize(older_datetime)
    newer_datetime = parse_datetime(newer_time if newer_time else localized_datetime_string_now())
    if not newer_datetime.tzinfo:
        newer_datetime = pytz.UTC.localize(newer_datetime)
    return (newer_datetime - older_datetime).total_seconds()

