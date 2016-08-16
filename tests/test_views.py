from idbase.views import login, logout, index
from idbase.models import UwUser
import pytest
from mock import patch, ANY
from django.shortcuts import render


@pytest.fixture
def req(rf, session):
    """A login request with an authenticated user"""
    return _get_request(rf, '/login/', session=session)


def test_index(req):
    with patch('idbase.views.render', side_effect=render) as mock_render:
        response = index(req)
        assert response.status_code == 200
        mock_render.assert_called_once_with(req, 'idbase/index.html', ANY)


def test_nonav(req):
    with patch('idbase.views.render', side_effect=render) as mock_render:
        response = index(req, template='nonav')
        assert response.status_code == 200
        mock_render.assert_called_once_with(req, 'idbase/nonav.html', ANY)


def test_login_redirect(req):
    req.session['_uw_postlogin'] = '/home'
    response = login(req)
    assert response.status_code == 302
    assert response['Location'] == '/home'


def test_login_unauthenticated(req):
    req.uw_user = UwUser()
    response = login(req)
    assert response.status_code == 401
    assert req.session._session == {}


def test_login_not_uw(req):
    req.uw_user = UwUser(username='joe@uw.edu')
    with patch('idbase.views.render', side_effect=render) as mock_render:
        response = login(req)
        assert response.status_code == 401
        assert req.session._session == {}
        mock_render.assert_called_once_with(req, ANY, status=401,
                                            context=dict(non_uw_user=True))


def test_login_non_person(req):
    req.uw_user = UwUser(username='robot@washington.edu', is_uw=True,
                         netid='robot', is_person=False)
    with patch('idbase.views.render', side_effect=render) as mock_render:
        response = login(req)
        assert response.status_code == 401
        assert req.session._session == {}
        mock_render.assert_called_once_with(req, ANY, status=401,
                                            context=dict(non_person='robot'))


@patch('idbase.views.render', side_effect=render)
def test_logout_clear_cookie(mock_render, rf):
    req = _get_request(rf, '/logout')
    req.COOKIES['foo'] = 'bar'
    response = logout(req)
    assert response.status_code == 200
    mock_render.assert_called_once_with(req, 'idbase/logout.html')
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


@patch('idbase.views.render', side_effect=render)
def test_logout_unsafe_next(mock_render, rf):
    req = _get_request(rf, '/logout?next=https://example.com')
    response = logout(req)
    assert response.status_code == 200
    mock_render.assert_called_once_with(req, 'idbase/logout.html')


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
    req.uw_user = lambda: None
    req.uw_user.username = 'joe@washington.edu'
    req.uw_user.is_authenticated = True
    req.session = session
    return req
