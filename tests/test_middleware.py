from idbase.middleware import LoginUrlMiddleware, SessionTimeoutMiddleware
import pytest
from importlib import import_module


@pytest.fixture
def session(settings):
    engine = import_module('django.contrib.sessions.backends.signed_cookies')
    store = engine.SessionStore()
    store['active'] = True  # set something so we can check if it's cleared.
    store.modified = False
    return store


def test_login_url_middleware_is_login_url(settings, rf, session):
    settings.LOGIN_URL = '/foo/login'
    request = rf.get('/foo/login')
    request.session = session
    request.META.update({'REMOTE_USER': 'foo@washington.edu'})
    LoginUrlMiddleware().process_request(request)
    assert request.user.is_authenticated()
    assert request.user.netid == 'foo'
    assert request.session._session == {
        '_login_url_remote_user': {'remote_user': 'foo@washington.edu'}}


def test_login_url_middleware_existing_user(settings, rf, session):
    settings.LOGIN_URL = '/foo/login'
    request = rf.get('/foo')
    session['_login_url_remote_user'] = {
        'remote_user': 'javerage@washington.edu'}
    request.session = session
    LoginUrlMiddleware().process_request(request)
    assert request.user.is_authenticated()
    assert request.user.netid == 'javerage'
    assert request.session._session == {
        'active': True,
        '_login_url_remote_user': {'remote_user': 'javerage@washington.edu'}}


def test_login_url_middleware_no_user(settings, rf, session):
    settings.LOGIN_URL = '/foo/login'
    request = rf.get('/foo')
    request.session = session
    LoginUrlMiddleware().process_request(request)
    assert not request.user.is_authenticated()


def test_login_url_middleware_login_page_unprotected(settings, rf, session):
    """A case where someone set a login page that's not SSO-protected."""
    settings.LOGIN_URL = '/foo/login'
    request = rf.get('/foo/login')
    request.session = session
    LoginUrlMiddleware().process_request(request)
    assert not request.user.is_authenticated()
    assert request.session._session == {
        '_login_url_remote_user': {'remote_user': ''}}
