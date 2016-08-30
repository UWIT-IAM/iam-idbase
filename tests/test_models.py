from idbase.models import BaseModel
from pytest import raises, mark


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
