from idbase.views import login
from idbase.exceptions import InvalidSessionError
import pytest


@pytest.fixture
def req(rf, session):
    """A login request with an authenticated user"""
    req = rf.get('/login/?next=/home')
    req.user = lambda: None
    req.user.username = 'joe@washington.edu'
    req.user.is_authenticated = lambda: True
    req.user.get_full_name = lambda: None
    req.user.set_full_name = lambda x: None
    req.session = session
    return req


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
