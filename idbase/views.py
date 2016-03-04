from django.shortcuts import render, redirect
from django.conf import settings
from idbase.exceptions import InvalidSessionError
import logging
from importlib import import_module

logger = logging.getLogger(__name__)


def index(request, template=None):
    """Render the Identity home page."""
    conf = {'urls': settings.CORE_URLS,
            'session_timeout': settings.SESSION_TIMEOUT_DEFAULT_SECONDS}

    return render(request, 'idbase/index.html', conf)


def login(request):
    """This view gets SSO-protected and redirects to next."""
    if request.user.is_authenticated():
        logger.info('User %s logged in' % (request.user.username))
        if (request.user.get_full_name() is None and
                hasattr(settings, 'GET_FULL_NAME_FUNCTION')):
            mod, func = settings.GET_FULL_NAME_FUNCTION.rsplit('.', 1)
            module = import_module(mod)
            full_name_function = getattr(module, func)
            request.user.set_full_name(full_name_function(request))
        return redirect(request.GET.get('next', '/'))
    else:
        raise InvalidSessionError('no REMOTE_USER variable set')
