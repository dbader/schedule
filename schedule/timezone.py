import datetime


class UTC(datetime.tzinfo):
    """tzinfo derived concrete class named "UTC" with offset of 0"""
    # can be configured here
    _offset = datetime.timedelta(seconds=0)
    _dst = datetime.timedelta(0)
    _name = "UTC"

    def utcoffset(self, dt):
        return self.__class__._offset

    def dst(self, dt):
        return self.__class__._dst

    def tzname(self, dt):
        return self.__class__._name
