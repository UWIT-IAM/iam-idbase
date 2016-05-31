from idbase.middleware import LoginUrlMiddleware, SessionTimeoutMiddleware
import pytest
from django.core.exceptions import ImproperlyConfigured


@pytest.fixture(autouse=True)
def settings(settings):
    settings.LOGIN_URL = '/foo/login'
    settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = True
    return settings


@pytest.fixture
def req(rf, session):
    """A mock Django request get with a mock session."""
    request = rf.get('/')
    request.session = session
    return request


def test_login_url_middleware_is_login_url(rf, session):
    request = rf.get('/foo/login')
    request.session = session
    request.META.update({
        'REMOTE_USER': 'foo@washington.edu',
        'Shib-Identity-Provider': 'urn:mace:incommon:washington.edu'})
    LoginUrlMiddleware().process_request(request)
    assert request.user.is_authenticated()
    assert request.user.netid == 'foo'
    assert request.session._session == {
        '_login_url_remote_user': dict(
            username='foo@washington.edu', netid='foo', authenticated=True,
            is_uw=True, is_person=True
        )}


def test_login_url_middleware_bad_idp(rf, session):
    request = rf.get('/foo/login')
    request.session = session
    request.META.update({
        'REMOTE_USER': 'foo@washington.edu',
        'Shib-Identity-Provider': 'google.com'})
    LoginUrlMiddleware().process_request(request)
    assert not request.user.is_authenticated()


def test_login_url_middleware_bad_session_data(req):
    req.session['_login_url_remote_user'] = dict(
        remote_user='joe@washington.edu')
    LoginUrlMiddleware().process_request(req)
    assert not req.user.is_authenticated()


def test_login_url_middleware_existing_user(req):
    req.session['_login_url_remote_user'] = {
        'username': 'javerage@washington.edu',
        'netid': 'javerage',
        'authenticated': True
    }
    LoginUrlMiddleware().process_request(req)
    assert req.user.is_authenticated()
    assert req.user.netid == 'javerage'
    assert req.session._session == {
        'active': True,
        '_login_url_remote_user': dict(
            username='javerage@washington.edu', netid='javerage',
            authenticated=True)
    }


def test_login_url_middleware_no_user(req):
    LoginUrlMiddleware().process_request(req)
    assert not req.user.is_authenticated()


def test_login_url_middleware_login_page_unprotected(rf, session):
    """A case where someone set a login page that's not SSO-protected."""
    request = rf.get('/foo/login')
    request.session = session
    LoginUrlMiddleware().process_request(request)
    assert not request.user.is_authenticated()
    assert request.session._session == {
        '_login_url_remote_user': dict(
            authenticated=False, username='', netid='',
            is_person=False, is_uw=False
        )}


@pytest.fixture(autouse=True)
def mock_localized_datetime(monkeypatch):
    monkeypatch.setattr('idbase.middleware.localized_datetime_string_now',
                        lambda: 'just now')


@pytest.fixture(autouse=True)
def mock_date_diff(monkeypatch):
    monkeypatch.setattr('idbase.middleware.datetime_diff_seconds',
                        lambda x: (10
                                   if x in ('just now', 'just then')
                                   else (20*60) + 1))


def test_session_timeout_middleware_init(settings):
    settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False
    with pytest.raises(ImproperlyConfigured):
        SessionTimeoutMiddleware()


def test_session_timeout_middleware_process_request_active(req):
    SessionTimeoutMiddleware().process_request(req)
    assert req.session['active'] is True


def test_session_timeout_process_request_expired(req):
    req.session['_session_timeout_last_update'] = 'a while back'
    SessionTimeoutMiddleware().process_request(req)
    assert 'active' not in req.session


def test_session_timeout_active_session(req):
    req.session['_session_timeout_last_update'] = 'just then'
    SessionTimeoutMiddleware().process_request(req)
    assert req.session['active'] is True


def test_session_timeout_default(req, settings):
    req.session['_session_timeout_last_update'] = 'just then'
    settings.SESSION_TIMEOUT_DEFAULT_SECONDS = 10
    SessionTimeoutMiddleware().process_request(req)
    assert req.session['active'] is True
    settings.SESSION_TIMEOUT_DEFAULT_SECONDS = 9
    SessionTimeoutMiddleware().process_request(req)
    assert 'active' not in req.session


def test_session_process_response_modified(req):
    req.session['updated'] = True
    assert SessionTimeoutMiddleware().process_response(req, 'blah') == 'blah'
    assert req.session['_session_timeout_last_update'] == 'just now'


def test_sesssion_process_response_unmodified(req):
    assert SessionTimeoutMiddleware().process_response(req, 'blah') == 'blah'
    assert '_session_timeout_last_update' not in req.session
