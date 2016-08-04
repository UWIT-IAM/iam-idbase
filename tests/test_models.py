from idbase.models import LoginUrlRemoteUser, BaseModel
from pytest import raises, mark
from django.contrib.auth.decorators import login_required


def test_login_url_remote_user_no_auth():
    user = LoginUrlRemoteUser()
    assert not user.is_authenticated


def test_login_url_remote_user_basic():
    user = LoginUrlRemoteUser(username='foo@washington.edu',
                              is_authenticated=True, netid='foo')
    assert user.is_authenticated
    assert user.get_username() == 'foo@washington.edu'
    assert user.netid == 'foo'


def test_login_url_model_with_login_required(rf):
    """
    Make sure our LoginUrlRemoteUser is handled correctly by Django 1.10
    login_required. 1.10 changed their model such that is_authenticated
    is an attribute rather than a method. Failure to adapt our model would
    mean the method is_authenticated would evaluate to True.
    """
    @login_required
    def fake_view(request):
        return 'is_auth'
    req = rf.get('/')
    req.user = LoginUrlRemoteUser()
    response = fake_view(req)
    assert response.status_code == 302
    req.user.is_authenticated = True
    assert fake_view(req) == 'is_auth'


class FooModel(BaseModel):
    netid = None
    sub_foo = None
    _specials = {'sub_foo': 'test_models.FooSubModel'}


class FooSubModel(BaseModel):
    netid = None


def test_base_model_no_dict():
    model = FooModel()
    assert model.netid is None
    assert model.sub_foo is None


def test_base_model_good_dict():
    model = FooModel(netid='joe', sub_foo=dict(netid='blow'))
    assert model.netid == 'joe'
    assert model.sub_foo.netid == 'blow'


def test_base_model_to_dict():
    model = FooModel(netid='joe', sub_foo=dict(netid='blow'))
    assert model.to_dict() == {'netid': 'joe', 'sub_foo': {'netid': 'blow'}}


def test_base_model_to_dict_no_sub():
    model = FooModel(netid='joe')
    assert model.to_dict() == {'netid': 'joe', 'sub_foo': None}


@mark.parametrize('dct', [
    {'netid': 'joe', 'name': 'bad'},
    {'netid': 'joe', 'sub_foo': {'bad': 'bad'}},
    {'netid': 'joe', '_hidden': 'bad'},
    {'netid': 'joe', 'sub_foo': {'_hidden': 'bad'}}],
    ids=['bad attribute', 'bad sub attribute', 'underscore attibute',
         'underscore sub attibute'])
def test_base_model_bad_dict(dct):
    with raises(ValueError):
        FooModel(**dct)
