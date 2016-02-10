from django.shortcuts import render, redirect
from django.conf import settings
from idbase.exceptions import InvalidSessionError
import logging

logger = logging.getLogger(__name__)


def index(request, template=None):
    """Render the Identity home page."""
    conf = {'urls': settings.CORE_URLS}

    return render(request, 'idbase/index.html', conf)


def login(request):
    """This view gets SSO-protected and redirects to next."""
    if request.user.is_authenticated():
        logger.info('User %s logged in' % (request.user.username))
        return redirect(request.GET.get('next', '/'))
    else:
        raise InvalidSessionError('no REMOTE_USER variable set')
