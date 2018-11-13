import datetime


class UTC(datetime.tzinfo):
    """tzinfo derived concrete class named "UTC" with offset of 0"""
    # can be changed to another timezone name/offset
    def __init__(self):
        self.__offset = datetime.timedelta(seconds=0)
        self.__dst = datetime.timedelta(0)
        self.__name = "UTC"

    def utcoffset(self, dt):
        return self.__offset

    def dst(self, dt):
        return self.__dst

    def tzname(self, dt):
        return self.__name
