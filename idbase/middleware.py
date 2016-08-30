from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from idbase.util import localized_datetime_string_now, datetime_diff_seconds
from idbase.util import get_class
import logging
from idbase.exceptions import InvalidSessionError, LoginNotPerson, ServiceError
from idbase.decorators import POSTLOGIN_KEY

logger = logging.getLogger(__name__)


UW_SAML_ENTITY = getattr(settings, 'SAML_ENTITIES', {}).get(
    'uw', 'urn:mace:incommon:washington.edu')


def get_authenticated_uwnetid(remote_user='', saml_idp=''):
    """
    Given a remote_user and saml_idp, return a personal UWNetID or raise
    an Exception.
    """
    if not remote_user:
        raise ServiceError('No REMOTE_USER variable set')
    if (not remote_user.endswith('@washington.edu') or
            saml_idp != UW_SAML_ENTITY):
        raise InvalidSessionError(
            'unauthenticated user id={id}, idp={idp}'.format(
                id=remote_user, idp=saml_idp))
    netid = remote_user.rsplit('@washington.edu', 1)[0]
    if not is_personal_netid(netid=netid):
        raise LoginNotPerson(
            'non-person logging in to site, REMOTE_USER={}'.format(
                remote_user),
            netid=netid)
    return netid


def is_personal_netid(netid=None):
    """
    Check in IRWS that a given netid belongs to a person. Non-persons
    don't get to log in.
    """
    irws = get_class(settings.IDBASE_IRWS_CLASS)()
    regid = irws.get_regid(netid=netid)
    return regid and regid.entity_name == 'Person'


class LoginUrlMiddleware(object):
    """
    Middleware to check the REMOTE_USER variable only when on LOGIN_URL,
    storing the user in the session. This should negate the need for
    AuthenticationMiddleware, RemoteUserMiddleware, and the associated
    AUTHENTICATION_BACKENDS.

    In this scenario, we have a login page that is protected by SSO,
    and multiple other SSO-protected pages that check federation status.
    Authenticate only the REMOTE_USER variable when on the configured
    LOGIN_URL.

    We store only authenticated personal UWNetIDs as request.uwnetid, or
    None if not authenticated. All errors are stored in request.login_url_error
    for handling in views.login.
    """
    UWNETID_KEY = '_login_url_uwnetid'

    def process_request(self, request):
        """
        Create a new login if on LOGIN_URL. Otherwise use an existing user if
        stored in the session.
        """
        if request.path == settings.LOGIN_URL:
            self.flush_session(request)
            try:
                uwnetid = get_authenticated_uwnetid(
                    remote_user=request.META.get('REMOTE_USER', ''),
                    saml_idp=request.META.get('Shib-Identity-Provider', ''))
                request.session[self.UWNETID_KEY] = uwnetid
            except (LoginNotPerson, InvalidSessionError) as e:
                logger.info(e)
                request.login_url_error = e
            except Exception as e:
                logger.exception(e)
                request.login_url_error = e
        request.uwnetid = request.session.get(self.UWNETID_KEY, None)

    @staticmethod
    def flush_session(request):
        postlogin_url = request.session.pop(POSTLOGIN_KEY, default=None)
        request.session.flush()
        if postlogin_url:
            request.session[POSTLOGIN_KEY] = postlogin_url


class SessionTimeoutMiddleware(object):
    """
    Middleware to supplement built-in session expiration with an
    independently-managed timeout. This allows us to set
    SESSION_EXPIRE_AT_BROWSER_CLOSE to True while also having an expiration,
    something the default session management doesn't allow for. Allows for
    setting SESSION_TIMEOUT_DEFAULT_SECONDS, the absence of which will set a
    timeout of 20 minutes.
    """
    def __init__(self):
        if not settings.SESSION_EXPIRE_AT_BROWSER_CLOSE:
            raise ImproperlyConfigured(
                'SessionTimeoutMiddleware expects '
                'SESSION_EXPIRE_AT_BROWSER_CLOSE to be True.')

    def process_request(self, request):
        """
        Invalidate a session if expiration is beyond the last session update.
        """
        last_update = request.session.get('_session_timeout_last_update',
                                          localized_datetime_string_now())

        expiry = getattr(settings, 'SESSION_TIMEOUT_DEFAULT_SECONDS', 20*60)

        diff = datetime_diff_seconds(last_update)
        if diff > expiry:
            logger.info(
                'Clearing session on inactivity (diff={}, expiry={})'.format(
                    diff, expiry))
            request.session.flush()

    def process_response(self, request, response):
        """
        Reset the timeout if the session has been modified.
        """
        if request.session.modified:
            request.session['_session_timeout_last_update'] = \
                localized_datetime_string_now()
        return response


class MockLoginMiddleware(object):
    """
    Middleware to fake a shib-protected LOGIN_URL.
    """
    def __init__(self):
        if not settings.DEBUG:
            logger.error('MockLoginMiddleware shouldn\'t be set in a '
                         'production environment')
        if not hasattr(settings, 'MOCK_LOGIN_USER'):
            raise ImproperlyConfigured('MOCK_LOGIN_USER required.')

    def process_request(self, request):
        """
        Set a remote_user if on LOGIN_URL.
        """
        if request.path == settings.LOGIN_URL:
            request.META.setdefault('REMOTE_USER', settings.MOCK_LOGIN_USER)
            request.META.setdefault('Shib-Identity-Provider', UW_SAML_ENTITY)
