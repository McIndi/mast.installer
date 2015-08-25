#!/usr/bin/env python

from time import time
from datetime import datetime


class Timestamp(object):
    """Timestamp an object which represents a given moment in time. An instance
    of Timestamp takes the time at initialization and captures the moment in
    epoch format using time.time(), after initialization, a number of
    convenience methods allow access to different formats of representing that
    time."""
    def __init__(self):
        """Initialization function, catpture the current time in epoch format
        then create a timestamp object from datetime.fromtimestamp()."""
        self._epoch = time()
        self._timestamp = datetime.fromtimestamp(self._epoch)

    @property
    def epoch(self):
        """Returns the timestamp in epoch format."""
        return int(self)

    @property
    def friendly(self):
        """Returns the timestamp in a friendly, human-readable format."""
        return self._timestamp.strftime('%A %B %d, %X')

    @property
    def timestamp(self):
        """Returns the timestamp in a special format which for jan 1, 1970 at
        midnight would look like this 1"9700101000000" which is year, month,
        day, hour, minute and second. This is very useful for timestamped
        filenames, where, you don't want commas and spaces, but would like
        something a human can read."""
        return self._timestamp.strftime('%Y%m%d%H%M%S')

    @property
    def short(self):
        """Returns the short representation of the timestamp, which for Jan 1,
        1970 at midnight would look like this "01-01-1970 00:00:00" """
        return self._timestamp.strftime('%m-%d-%Y %H:%M:%S')

    def strftime(self, _format):
        """Return the timestamp in a format specified by the _format param.
        This should be a string following the rules here:

            https://docs.python.org/2/library/datetime.html#\
            strftime-and-strptime-behavior"""
        return self._timestamp.strftime(_format)

    def __str__(self):
        """This ensures that when doing something like:

            print Timestamp()

        you get a human-readable version."""
        return self.friendly

    def __int__(self):
        """this ensures that this will work:

            import timestamp
            t1 = timestamp.Timestamp()

            do_something()

            t2 = timestamp.Timestamp()
            print "The operation took {} seconds to complete".format(t1 - t2)"""
        return int(self._epoch)

if __name__ == '__main__':
    ts = Timestamp()
    print ts.timestamp
    print ts.friendly
    print ts.epoch
