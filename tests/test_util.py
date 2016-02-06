from idbase.util import localized_datetime_string_now, datetime_diff_seconds
from mock import patch
import re


def test_localized_datetime_string_now_pacific_time(settings):
    settings.TIME_ZONE = 'America/Los_Angeles'
    local_time = localized_datetime_string_now()
    assert local_time.endswith('-07:00') or local_time.endswith('-08:00')


def test_localized_datetime_string_now_no_microseconds(settings):
    """
    Test that our datetime doesn't have microsecond precision, which IRWS
    doesn't have space for.
    """
    settings.TIME_ZONE = 'America/Los_Angeles'
    local_time = localized_datetime_string_now()
    assert re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}-0[78]:00', local_time)


def test_datetime_diff_seconds_one_hour():
    assert datetime_diff_seconds('2015-10-15T12:07:07.055934-07:00',
                                 '2015-10-15T13:07:07.055934-07:00') == 3600

def test_datetime_diff_seconds_naive_older_time():
    assert datetime_diff_seconds('2015-10-15T06:00:00',
                                 newer_time='2015-10-15T00:00:00.0-07:00') == 3600


def test_datetime_diff_seconds_naive_newer_time():
    assert datetime_diff_seconds('2015-10-15T00:00:00-07:00',
                                 newer_time='2015-10-15T08:00:00') == 3600


def test_datetime_diff_implicit_now():
    with patch('idbase.util.localized_datetime_string_now') as mock_now:
        mock_now.return_value = '2015-10-15T08:00:00.0-07:00'
        assert datetime_diff_seconds('2015-10-15T07:00:00.0-07:00') == 3600