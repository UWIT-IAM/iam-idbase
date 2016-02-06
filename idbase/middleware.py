from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from idbase.util import localized_datetime_string_now, datetime_diff_seconds
from idbase.models import LoginUrlRemoteUser
import logging

logger = logging.getLogger(__name__)


class LoginUrlMiddleware(object):
    """
    Middleware to check the REMOTE_USER variable only when on LOGIN_URL,
    storing the user in the session. This should negate the need for
    AuthenticationMiddleware, RemoteUserMiddleware, and the associated
    AUTHENTICATION_BACKENDS.

    In this scenario, we have a login page that is protected by SSO, and
    multiple other SSO-protected pages that check federation status. Authenticate
    only the REMOTE_USER variables on the configured LOGIN_URL.
    """
    def process_request(self, request):
        """
        Create a new login if on LOGIN_URL. Otherwise use an existing user if stored
        in the session.
        """
        if request.path == settings.LOGIN_URL:
            remote_user = request.META.get('REMOTE_USER', '')
            logger.info('authenticating ' + remote_user)
            request.session.flush()
            user = LoginUrlRemoteUser(remote_user=remote_user)
        else:
            # Empty dictionary creates an unauthenticated user.
            user = LoginUrlRemoteUser(**request.session.get('_login_url_remote_user', {}))
        request.user = user

    def process_response(self, request, response):
        """
        Store an authenticated user on the session.
        """
        if request.user.is_authenticated():
            user = dict(remote_user=request.user.username, full_name=request.user.full_name)
            if user != request.session.get('_login_url_remote_user', {}):
                # Only update the session if something changed.
                request.session['_login_url_remote_user'] = user
        return response


class SessionTimeoutMiddleware(object):
    """
    Middleware to supplement built-in session expiration with an
    independently-managed timeout. This allows us to set
    SESSION_EXPIRE_AT_BROWSER_CLOSE to True while also having an expiration,
    something the default session management doesn't allow for. Allows for setting
    SESSION_TIMEOUT_DEFAULT_SECONDS, the absence of which will set a timeout of 20 minutes.
    """
    def __init__(self):
        if not settings.SESSION_EXPIRE_AT_BROWSER_CLOSE:
            raise ImproperlyConfigured(
                'SessionTimeoutMiddleware expects SESSION_EXPIRE_AT_BROWSER_CLOSE'
                ' to be True.')

    def process_request(self, request):
        """
        Invalidate a session if expiration is beyond the last session update.
        """
        last_update = request.session.get('_session_timeout_last_update', localized_datetime_string_now())

        # First check the session for an expiry, then the settings, then default to 20 minutes
        expiry = request.session.get('_session_timeout_expiry', 0)
        if not expiry:
            expiry = getattr(settings, 'SESSION_TIMEOUT_DEFAULT_SECONDS', 20*60)

        diff = datetime_diff_seconds(last_update)
        logger.info('Comparing last update diff of {diff} to expiry {expiry}'.format(diff=diff, expiry=expiry))
        if diff > expiry:
            logger.info('clearing session on inactivity')
            request.session.flush()

    def process_response(self, request, response):
        """
        Reset the timeout if the session has been modified.
        """
        if request.session.modified:
            request.session['_session_timeout_last_update'] = localized_datetime_string_now()
        return response

    def set_expiry(self, request, age=20*60):
        """
        Set an expiration at run-time to one shorter or longer than the default.
        """
        request.session['_session_timeout_expiry'] = age