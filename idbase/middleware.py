from django.conf import settings
import logging
import re

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


class LoginUrlRemoteUser(object):
    """
    An implementation of the django User interface that doesn't save to
    or retrieve from a database.
    """

    _is_authenticated = False
    username = ''
    netid = ''
    full_name = None

    def __init__(self, remote_user=None, full_name=None, **kwargs):
        """
        Initialize a user, giving a remote_user if an authenticated user.
        """
        if remote_user:
            self._is_authenticated = True
            self.username = remote_user
            if remote_user and remote_user.endswith('@washington.edu'):
                self.netid = re.sub(r'@washington.edu$', '', remote_user)
            self.full_name = full_name

    def get_username(self):
        return self.username

    def is_authenticated(self):
        return self._is_authenticated

    def get_full_name(self):
        return self.full_name
