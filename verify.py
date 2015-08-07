from resttools.irws import IRWS
from django.conf import settings

def match_student_pac(uwnetid, pac):
    irws = IRWS(settings.IRWS_CONF)
    response = irws.get_person(netid=uwnetid)
    return False