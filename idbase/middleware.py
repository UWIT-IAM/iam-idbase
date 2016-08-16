from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from idbase.util import localized_datetime_string_now, datetime_diff_seconds
from idbase.util import get_class
from idbase.models import UwUser
import logging

logger = logging.getLogger(__name__)


UW_SAML_ENTITY = getattr(settings, 'SAML_ENTITIES', {}).get(
    'uw', 'urn:mace:incommon:washington.edu')


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
    """
    def process_request(self, request):
        """
        Create a new login if on LOGIN_URL. Otherwise use an existing user if
        stored in the session.
        """
        if request.path == settings.LOGIN_URL:
            postlogin_url = request.session.pop('_uw_postlogin', default=None)
            request.session.flush()
            user = UwUser()
            user.username = request.META.get('REMOTE_USER', '')
            saml_idp = request.META.get('Shib-Identity-Provider', '')
            if (user.username.endswith('@washington.edu') and
                    saml_idp == UW_SAML_ENTITY):
                user.netid = user.username.rsplit(
                    '@washington.edu', 1)[0]
                user.is_person = self._is_person(netid=user.netid)
                user.is_uw = True
                logger.info('authenticating ' + user.username)
                # a user is only authenticated if is_uw and is_person
                user.is_authenticated = user.is_person
            else:
                logger.info('unauthenticated user id={id}, idp={idp}'.format(
                    id=user.username, idp=saml_idp))
            request.session['_uw_user'] = user.to_dict()
            if postlogin_url:
                request.session['_uw_postlogin'] = postlogin_url
            request.uw_user = user
        else:
            try:
                request.uw_user = UwUser(
                    **request.session.get('_uw_user', {}))
            except:
                request.uw_user = UwUser()

    def _is_person(self, netid=None):
        """
        Check that the netid given is a personal netid. Return True with an
        error message for incomplete settings.
        """
        if not hasattr(settings, 'IDBASE_IRWS_CLASS'):
            logger.error('Undefined setting IDBASE_IRWS_CLASS'
                         ' disables the login check for person')
            return True
        irws = get_class(settings.IDBASE_IRWS_CLASS)()
        regid = irws.get_regid(netid=netid)
        return regid and regid.entity_name == 'Person'


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
