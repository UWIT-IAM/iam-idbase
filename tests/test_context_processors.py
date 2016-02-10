from idbase.context_processors import app_context
import pytest


@pytest.fixture
def req(rf):
    req = rf.get('/')
    req.resolver_match = lambda: None
    req.resolver_match.namespace = 'home'
    return req


@pytest.fixture(autouse=True)
def settings(settings):
    settings.DEBUG = True
    settings.APP_CONTEXTS = {
        'default': {'base_url': '/default/', 'css_loads': ['blah'],
                    'javascript_loads': ['blah']},
        'home': {'base_url': '/home/', 'css_loads': ['home.css'],
                 'javascript_loads': ['home.js']},
    }
    return settings


def test_app_context_default(req, settings):
    delattr(settings, 'APP_CONTEXTS')
    assert app_context(req) == {
        'app': {'base_url': '/', 'css_loads': [],
                'javascript_loads': [], 'debug': True}}


def test_app_context_default_setting(req):
    req.resolver_match.namespace = 'nothing'
    assert app_context(req) == {
        'app': {'base_url': '/default/', 'css_loads': ['blah'],
                'javascript_loads': ['blah'], 'debug': True}}


def test_app_context_namespace(req):
    assert app_context(req) == {
        'app': {'base_url': '/home/', 'css_loads': ['home.css'],
                'javascript_loads': ['home.js'], 'debug': True}}
