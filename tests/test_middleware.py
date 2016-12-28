from idbase.middleware import (login_url_middleware,
                               session_timeout_middleware,
                               mock_login_middleware,
                               get_authenticated_uwnetid)
from pytest import fixture, raises, mark
from django.core.exceptions import ImproperlyConfigured
from idbase.exceptions import InvalidSessionError, LoginNotPerson, ServiceError


@fixture(autouse=True)
def settings(settings):
    settings.LOGIN_URL = '/foo/login'
    settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = True
    return settings


@fixture
def req_func(rf, session):
    def func(url='/'):
        request = rf.get(url)
        request.session = session
        return request
    return func


@fixture
def login_req(req_func):
    req = req_func(url='/foo/login')
    req.META.update({
        'REMOTE_USER': 'foo@washington.edu',
        'Shib-Identity-Provider': 'urn:mace:incommon:washington.edu'})
    req.session['_uw_postlogin'] = '/home'
    return req


@fixture
def req(req_func):
    """A mock Django request get with a mock session."""
    return req_func()


def test_login_url_middleware_is_login_url(login_req):
    login_url_middleware(gr)(login_req)
    assert login_req.uwnetid == 'foo'
    assert login_req.session._session == {
        '_login_url_uwnetid': 'foo',
        '_uw_postlogin': '/home'
    }


def test_login_url_middleware_bad_idp(login_req):
    login_req.META['Shib-Identity-Provider'] = 'google.com'
    login_url_middleware(gr)(login_req)
    assert not login_req.uwnetid
    assert isinstance(login_req.login_url_error, InvalidSessionError)


def test_login_url_middleware_existing_user(req):
    req.session['_login_url_uwnetid'] = 'javerage'
    login_url_middleware(gr)(req)
    assert req.uwnetid == 'javerage'


def test_login_url_middleware_no_user(req):
    login_url_middleware(gr)(req)
    assert not req.uwnetid


def test_login_url_middleware_login_page_unprotected(login_req):
    """A case where someone set a login page that's not SSO-protected."""
    login_req.META = {}
    login_req.session.flush()
    login_url_middleware(gr)(login_req)
    assert not login_req.uwnetid
    assert login_req.session._session == {}


def test_login_url_middleware_broken_irws(login_req, monkeypatch):

    def blowup(self, netid=None):
        raise Exception()
    monkeypatch.setattr('idbase.mock.IRWS.get_regid', blowup)
    login_url_middleware(gr)(login_req)
    assert not login_req.uwnetid
    assert isinstance(login_req.login_url_error, Exception)


def test_get_authenticated_uwnetid_basic(monkeypatch):
    monkeypatch.setattr('idbase.middleware.is_personal_netid',
                        lambda **args: True)
    netid = get_authenticated_uwnetid(
        remote_user='joe@washington.edu',
        saml_idp='urn:mace:incommon:washington.edu')
    assert netid == 'joe'


@mark.parametrize('remote_user,saml_idp,is_person,expected_error', [
    ('', '', True, ServiceError),
    ('joe@washington.edu', 'google.com', True, InvalidSessionError),
    ('joe', 'urn:mace:incommon:washington.edu', True, InvalidSessionError),
    ('joe@washington.edu', 'urn:mace:incommon:washington.edu', False,
     LoginNotPerson)])
def test_get_authenticated_uwnetid_error(
        remote_user, saml_idp, is_person, expected_error, monkeypatch):
    monkeypatch.setattr('idbase.middleware.is_personal_netid',
                        lambda **args: is_person)
    with raises(expected_error):
        get_authenticated_uwnetid(remote_user=remote_user, saml_idp=saml_idp)


@fixture(autouse=True)
def mock_localized_datetime(monkeypatch):
    monkeypatch.setattr('idbase.middleware.localized_datetime_string_now',
                        lambda: 'just now')


@fixture(autouse=True)
def mock_date_diff(monkeypatch):
    monkeypatch.setattr('idbase.middleware.datetime_diff_seconds',
                        lambda x: (10
                                   if x in ('just now', 'just then')
                                   else (20 * 60) + 1))


def test_session_timeout_middleware_init(settings):
    settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False
    with raises(ImproperlyConfigured):
        session_timeout_middleware(gr)


def test_session_timeout_middleware_process_request_active(req):
    session_timeout_middleware(gr)(req)
    assert req.session['active'] is True


def test_session_timeout_process_request_expired(req):
    req.session['_session_timeout_last_update'] = 'a while back'
    session_timeout_middleware(gr)(req)
    assert 'active' not in req.session


def test_session_timeout_active_session(req):
    req.session['_session_timeout_last_update'] = 'just then'
    session_timeout_middleware(gr)(req)
    assert req.session['active'] is True


def test_session_timeout_default(req, settings):
    req.session['_session_timeout_last_update'] = 'just then'
    settings.SESSION_TIMEOUT_DEFAULT_SECONDS = 10
    session_timeout_middleware(gr)(req)
    assert req.session['active'] is True
    settings.SESSION_TIMEOUT_DEFAULT_SECONDS = 9
    session_timeout_middleware(gr)(req)
    assert 'active' not in req.session


def test_session_process_response_modified(req):
    req.session['updated'] = True
    session_timeout_middleware(gr)(req)
    assert req.session['_session_timeout_last_update'] == 'just now'


def test_session_process_response_unmodified(req):
    session_timeout_middleware(gr)(req)
    assert '_session_timeout_last_update' not in req.session


def test_mock_login_middleware_enabled(req, settings):
    settings.USE_MOCK_LOGIN = True
    settings.MOCK_LOGIN_USER = 'foo@washington.edu'
    req.path = settings.LOGIN_URL
    mock_login_middleware(gr)(req)
    assert req.META.get('REMOTE_USER') == 'foo@washington.edu'
    assert (req.META.get('Shib-Identity-Provider') ==
            'urn:mace:incommon:washington.edu')


def test_mock_login_middleware_disabled(req, settings):
    settings.USE_MOCK_LOGIN = False

    req.path = settings.LOGIN_URL
    mock_login_middleware(gr)(req)
    assert not req.META.get('REMOTE_USER')


def gr(request):
    return request
