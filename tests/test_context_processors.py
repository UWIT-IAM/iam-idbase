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
                    'javascript_loads': ['blah'],
                    'logout_url': '/defaultlogout'},
        'home': {'base_url': '/home/', 'css_loads': ['home.css'],
                 'javascript_loads': ['home.js'],
                 'logout_url': '/homelogout'},
    }
    return settings


def test_app_context_default(req, settings):
    delattr(settings, 'APP_CONTEXTS')
    assert app_context(req) == {
        'app': {'base_url': '/', 'css_loads': [],
                'javascript_loads': [], 'debug': True,
                'logout_url': '/logout'}}


def test_app_context_default_setting(req):
    req.resolver_match.namespace = 'nothing'
    assert app_context(req) == {
        'app': {'base_url': '/default/', 'css_loads': ['blah'],
                'javascript_loads': ['blah'], 'debug': True,
                'logout_url': '/defaultlogout'}}


def test_app_context_namespace(req):
    assert app_context(req) == {
        'app': {'base_url': '/home/', 'css_loads': ['home.css'],
                'javascript_loads': ['home.js'], 'debug': True,
                'logout_url': '/homelogout'}}


def test_app_context_logout_setting(req, settings):
    settings.LOGOUT_URL = '/newlogout'
    [settings.APP_CONTEXTS[key].pop('logout_url')
     for key in settings.APP_CONTEXTS.keys()]
    assert app_context(req)['app']['logout_url'] == '/newlogout'
