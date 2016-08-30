from __future__ import absolute_import  # available in python 3+
from mock import MagicMock


class IRWS(object):

    def get_regid(self, netid=None):
        regid = MagicMock()
        regid.entity_name = 'Person'
        return regid
