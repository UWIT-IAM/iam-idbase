from idbase.views import login
from idbase.exceptions import InvalidSessionError
import pytest


@pytest.fixture
def req(rf):
    """A login request with an authenticated user"""
    req = rf.get('/login/?next=/home')
    req.user = lambda: None
    req.user.username = 'joe'
    req.user.is_authenticated = lambda: True
    req.user.get_full_name = lambda: None
    return req


def test_login_redirect(req):
    response = login(req)
    assert response.status_code == 302
    assert response['Location'] == '/home'


def test_login_unauthenticated(req):
    req.user.is_authenticated = lambda: False
    with pytest.raises(InvalidSessionError):
        login(req)
