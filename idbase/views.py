from django.shortcuts import render, redirect
from django.conf import settings
from django.utils.http import is_safe_url
import logging
import re

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
        next_url = request.GET.get('next', '/')
        return redirect(next_url if is_safe_url(next_url) else '/')
    else:
        # This can happen if a user gets past weblogin but comes in with
        # no attributes, which indicates a problem upstream.
        return _login_error(request)


def logout(request):
    """
    Logout a user by removing all cookies that don't have the magic string
    'persistent', and redirect to settings.LOGOUT_REDIRECT.
    """
    next_param = request.GET.get('next', None)
    next_url = (next_param
                if next_param and is_safe_url(next_param)
                else getattr(settings, 'LOGOUT_REDIRECT', None))
    response = (redirect(next_url)
                if next_url
                else render(request, 'idbase/logout.html'))
    logger.debug('Logging out {} and redirecting to {}'.format(
        request.user.username, next_url))
    # delete all cookies that don't contain the string 'persistent'
    delete_keys = [key for key in request.COOKIES
                   if not re.search(r'persistent', key, re.IGNORECASE)]
    for key in delete_keys:
        response.delete_cookie(key)

    return response


def _login_error(request):
    context = {}
    if not request.user.get_username():
        logger.error('No REMOTE_USER variable set')
    elif not request.user.is_uw:
        logger.error('incorrect idp!!, REMOTE_USER={}'.format(
            request.user.username))
        context['non_uw_user'] = True
    elif not request.user.is_person:
        logger.error('non-person logging in to site, REMOTE_USER={}'.format(
            request.user.username))
        context['non_person'] = request.user.netid

    # end of the road.
    request.session.flush()
    return render(request, 'idbase/login-error.html', status=401,
                  context=context)
