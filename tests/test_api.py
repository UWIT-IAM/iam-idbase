from idbase.api import RESTDispatch, LoginStatus
from idbase import exceptions
from idbase.models import UwUser
from django.http import HttpResponse
from mock import MagicMock
import pytest
import json


@pytest.fixture
def req(rf):
    request = rf.get('/')
    request.uw_user = UwUser(is_authenticated=True)
    return request


@pytest.fixture
def rest_dispatch():
    """Instantiate a RESTDispatch object with a GET method."""
    rd = RESTDispatch()
    rd.GET = MagicMock()
    rd.GET.side_effect = lambda x: {'foo': 'bar'}
    return rd


def test_rest_dispatch_run_get_basic(rest_dispatch, req):
    response = rest_dispatch.run(req)

    assert response.status_code == 200
    assert response.content.decode() == json.dumps({'foo': 'bar'})
    assert (response._headers['content-type'] ==
            ('Content-Type', 'application/json'))
    rest_dispatch.GET.assert_called_once_with(req)


def test_rest_dispatch_run_http_response(rest_dispatch, req):
    rest_dispatch.GET.side_effect = lambda x: HttpResponse(
        content='hello world', status=503)
    response = rest_dispatch.run(req)

    assert response.status_code == 503
    assert response.content.decode() == 'hello world'


def test_rest_dispatch_run_get_no_method(req):
    rd = RESTDispatch()
    response = rd.run(req)
    assert response.status_code == 400
    assert json.loads(response.content.decode()).get(
        'error_message', None) is not None


def test_rest_dispatch_run_invalid_session(rest_dispatch, req):
    rest_dispatch.GET.side_effect = exceptions.InvalidSessionError()
    response = rest_dispatch.run(req)
    assert response.status_code == 401


def test_rest_dispatch_run_not_found(rest_dispatch, req):
    rest_dispatch.GET.side_effect = exceptions.NotFoundError()
    response = rest_dispatch.run(req)
    assert response.status_code == 404


def test_rest_dispatch_run_exception(rest_dispatch, req):
    rest_dispatch.GET.side_effect = Exception()
    response = rest_dispatch.run(req)
    assert response.status_code == 500


def test_rest_dispatch_not_logged_in(rest_dispatch, req):
    req.uw_user.is_authenticated = False
    response = rest_dispatch.run(req)
    assert response.status_code == 401


def test_rest_dispatch_no_login_necessary(req):
    req.uw_user.is_authenticated = False
    rest_dispatch = RESTDispatch(login_required=False)
    rest_dispatch.GET = lambda x: {'foo': 'bar'}
    response = rest_dispatch.run(req)

    assert response.status_code == 200
    assert json.loads(response.content.decode()) == {'foo': 'bar'}


def test_rest_dispatch_with_login_model(rest_dispatch, req):
    req.uw_user = UwUser()
    assert rest_dispatch.run(req).status_code == 401
    req.uw_user.is_authenticated = True
    assert rest_dispatch.run(req).status_code == 200


def test_login_status_get(req):
    req.uw_user.netid = 'jo'
    assert LoginStatus().GET(req) == {'netid': 'jo'}


def test_login_status_no_auth(req):
    req.uw_user.is_authenticated = False
    with pytest.raises(exceptions.InvalidSessionError):
        LoginStatus().GET(req)
