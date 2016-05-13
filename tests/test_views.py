from idbase.views import login, logout
import pytest


@pytest.fixture
def req(rf, session):
    """A login request with an authenticated user"""
    return _get_request(rf, '/login/?next=/home', session=session)


def test_login_redirect(req):
    response = login(req)
    assert response.status_code == 302
    assert response['Location'] == '/home'


def test_login_unauthenticated(req):
    req.user.is_authenticated = lambda: False
    response = login(req)
    assert response.status_code == 401
    assert req.session._session == {}


def test_login_not_uw(req):
    req.user.username = 'joe@example.com'
    response = login(req)
    assert response.status_code == 401
    assert req.session._session == {}


def test_login_offsite(rf):
    req = _get_request(rf, '/login/?next=http://example.com')
    req.COOKIES['foo'] = 'bar'
    response = login(req)
    assert response.status_code == 302
    assert response['Location'] == '/'


def test_logout_clear_cookie(rf):
    req = _get_request(rf, '/logout')
    req.COOKIES['foo'] = 'bar'
    response = logout(req)
    assert response.status_code == 302
    assert response['Location'] == '/'
    assert response.cookies['foo'].value == ''


def test_logout_persistent_cookie(rf):
    req = _get_request(rf, '/logout')
    req.COOKIES.update({'foo': 'bar',
                        'fooPersistent': 'boop'})
    response = logout(req)
    assert response.cookies['foo'].value == ''
    # The absence of persistentFoo means the cookie was untouched
    assert 'fooPersistent' not in response.cookies


def test_logout_safe_next(rf):
    response = logout(_get_request(rf, '/logout?next=/home'))
    assert response.status_code == 302
    assert response['Location'] == '/home'


def test_logout_unsafe_next(rf):
    response = logout(_get_request(rf, '/logout?next=https://example.com'))
    assert response.status_code == 302
    assert response['Location'] == '/'


def test_logout_redirect(rf, settings):
    settings.LOGOUT_REDIRECT = 'https://example.com'
    response = logout(_get_request(rf, '/logout'))
    assert response.status_code == 302
    assert response['Location'] == 'https://example.com'


def test_logout_redirect_and_next(rf, settings):
    settings.LOGOUT_REDIRECT = 'https://example.com'
    response = logout(_get_request(rf, '/logout?next=/home'))
    assert response.status_code == 302
    assert response['Location'] == '/home'


def _get_request(rf, url, session=None):
    req = rf.get(url)
    req.user = lambda: None
    req.user.username = 'joe@washington.edu'
    req.user.is_authenticated = lambda: True
    req.user.get_full_name = lambda: None
    req.user.set_full_name = lambda x: None
    req.session = session
    return req
