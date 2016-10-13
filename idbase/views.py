from django.shortcuts import render, redirect
from django.conf import settings
from django.utils.http import is_safe_url
import logging
import re
from idbase.exceptions import LoginNotPerson, InvalidSessionError
from idbase.decorators import POSTLOGIN_KEY

logger = logging.getLogger(__name__)


def index(request, template=None):
    """Render the Identity home page."""
    conf = {'urls': settings.CORE_URLS,
            'session_timeout': settings.SESSION_TIMEOUT_DEFAULT_SECONDS}
    page = 'idbase/{}.html'.format(template if template else 'index')
    return render(request, page, conf)


def login(request):
    """This view gets SSO-protected and redirects to next."""
    if request.uwnetid:
        logger.info('User %s@washington.edu logged in' % (request.uwnetid))
        next_url = request.session.pop(POSTLOGIN_KEY, default='/')
        return redirect(next_url if is_safe_url(next_url) else '/')
    else:
        error = getattr(request, 'login_url_error', None)
        status = 401
        context = {}
        if isinstance(error, LoginNotPerson):
            context['non_person'] = error.netid
        elif isinstance(error, InvalidSessionError):
            context['non_uw_user'] = True
        else:
            status = 500
        # end of the road.
        request.session.flush()
        return render(request, 'idbase/login-error.html', status=status,
                      context=context)


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
    logger.debug('Logging out {}@washington.edu and redirecting to {}'.format(
        request.uwnetid, next_url))
    # delete all cookies that don't contain the string 'persistent'
    delete_keys = [key for key in request.COOKIES
                   if not re.search(r'persistent', key, re.IGNORECASE)]
    for key in delete_keys:
        response.delete_cookie(key)

    return response
