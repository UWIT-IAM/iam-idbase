from idbase.views import login, logout, index
from idbase.exceptions import LoginNotPerson, InvalidSessionError
from pytest import fixture, mark
from mock import patch, ANY
from django.shortcuts import render


@fixture
def req(rf, session):
    """A login request with an authenticated user"""
    req = _get_request(rf, '/login/', session=session)
    req.uwnetid = None
    return req


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
    req.uwnetid = 'fake!!!'
    req.session['_uw_postlogin'] = '/home'
    response = login(req)
    assert response.status_code == 302
    assert response['Location'] == '/home'


@mark.parametrize('is_exception_raised', [True, False])
def test_login_error(req, is_exception_raised):
    if is_exception_raised:
        req.login_url_error = Exception()
    response = login(req)
    assert response.status_code == 500
    assert req.session._session == {}


def test_login_not_uw(req):
    req.login_url_error = InvalidSessionError()
    with patch('idbase.views.render', side_effect=render) as mock_render:
        response = login(req)
        assert response.status_code == 401
        assert req.session._session == {}
        mock_render.assert_called_once_with(req, ANY, status=401,
                                            context=dict(non_uw_user=True))


def test_login_non_person(req):
    req.uwnetid = None
    req.login_url_error = LoginNotPerson(netid='robot')
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
    req.uwnetid = 'joe'
    req.session = session
    return req
