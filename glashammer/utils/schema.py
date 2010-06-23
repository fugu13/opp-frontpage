
"""
    glashammer.utils.schema
    ~~~~~~~~~~~~~~~~~~~~~~~

    Flatland schema additions.

    :copyright: 2009-10 by Glashammer Developers
    :license: MIT
"""

from werkzeug import import_string
from flatland import String, Scalar, Dict, List, Integer, Boolean

class Any(Scalar):

    def adapt(self, value):
        return value

class Import(String):

    def adapt(self, value):
        value = String.adapt(self, value)
        if value is not None:
            try:
                value = import_string(str(value))
            except ImportError, e:
                msg = 'Warning, failed to import %r, %s' % (value, e)
                print msg
                raise AdaptationError(msg)
            return value

