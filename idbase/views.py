from django.shortcuts import render, redirect
from django.conf import settings
from django.utils.http import is_safe_url
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
        if not request.user.username.endswith('@washington.edu'):
            # Non-uw possibility when using a federated idp for recovery.
            return _login_error(request)
        if (request.user.get_full_name() is None and
                hasattr(settings, 'GET_FULL_NAME_FUNCTION')):
            mod, func = settings.GET_FULL_NAME_FUNCTION.rsplit('.', 1)
            module = import_module(mod)
            full_name_function = getattr(module, func)
            request.user.set_full_name(full_name_function(request))
        return _safe_redirect(request)
    else:
        # This can happen if a user gets past weblogin but comes in with
        # no attributes, which indicates a problem upstream.
        return _login_error(request)


def logout(request):
    response = _safe_redirect(request)
    logger.debug('Logging out {}'.format(request.user.username))
    for cookie in request.COOKIES.keys():
        response.delete_cookie(cookie)
    return response


def _safe_redirect(request):
    """Return a redirect response to the 'next' parameter if safe."""
    redirect_target = request.GET.get('next', '/')
    return redirect(redirect_target if is_safe_url(redirect_target) else '/')


def _login_error(request):
    context = {}
    if not request.user.is_authenticated():
        logger.error('No REMOTE_USER variable set')
    else:
        logger.error('incorrect idp!!, REMOTE_USER={}'.format(
            request.user.username))
        context['non_uw_user'] = True

    # end of the road.
    request.session.flush()
    return render(request, 'idbase/login-error.html', status=401,
                  context=context)
