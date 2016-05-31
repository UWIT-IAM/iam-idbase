from __future__ import absolute_import  # available in python 3+
from mock import MagicMock

mock_entity_name = 'Person'


def IRWS():
    irws = MagicMock()
    irws.get_regid.return_value.entity_name = mock_entity_name
    return irws
