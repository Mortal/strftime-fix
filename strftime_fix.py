# SPDX-License-Identifier: GPL-3.0-only
'''
Is your codebase riddled with strftime() using "%G-%m-%d"? Fear not!
Just import strftime_fix before importing datetime and you'll be all set!

>>> import strftime_fix
>>> import datetime
>>> datetime.datetime(year=2018, month=12, day=31).strftime('%G-%m-%d')
'2018-12-31'
>>> datetime.date(year=2018, month=12, day=31).strftime('%G-%m-%d')
'2018-12-31'
'''

from datetime import (
    MAXYEAR, MINYEAR, datetime_CAPI, time, timedelta, timezone, tzinfo,
)
import datetime as _real_datetime
import re as _re
import sys as _sys
_sys.modules['datetime'] = _sys.modules['strftime_fix']


__all__ = ['MAXYEAR', 'MINYEAR', 'date', 'datetime', 'datetime_CAPI',
           'time', 'timedelta', 'timezone', 'tzinfo']


class _datetime_meta(type):
    def __init__(self, name, bases, dict):
        super().__init__(name, bases, dict)
        try:
            self._inner = getattr(_real_datetime, self.__name__)
        except AttributeError:
            assert self.__name__.startswith('_')

    def _wrap(self, obj):
        if callable(obj):
            def _wrapped(*args, **kwargs):
                res = obj(*args, **kwargs)
                if isinstance(res, self._inner):
                    return self(res)
                return res

            return _wrapped
        return obj

    def __getattr__(self, k):
        return self._wrap(getattr(self._inner, k))

    def __dir__(self):
        return dir(self._inner)


class _base(metaclass=_datetime_meta):
    def __new__(cls, *args, **kwargs):
        try:
            (arg,), () = args, kwargs
        except ValueError:
            pass
        else:
            if isinstance(arg, cls._inner):
                return object.__new__(cls)
        return cls(cls._inner(*args, **kwargs))

    def __dir__(self):
        return self._inner.__dir__()

    def __init__(self, *a, **k):
        if '_inner' not in self.__dict__:
            (self._inner,), () = a, k

    def _wrap_instance(self, obj):
        if callable(obj):
            def _wrapped(*args, **kwargs):
                res = obj(*args, **kwargs)
                if isinstance(res, self.__class__._inner):
                    return self.__class__(res)
                return res

            return _wrapped
        return obj

    def __getattr__(self, k):
        return self._wrap_instance(getattr(self._inner, k))

    def strftime(self, s):
        s = _re.sub(
            r'%[YG]', lambda mo: '%Y' if mo.group(0) == '%G' else '%G', s)
        return self._inner.strftime(s)

    def __str__(self):
        return str(self._inner)

    def __repr__(self):
        return repr(self._inner)


class datetime(_base):
    pass


class date(_base):
    pass
