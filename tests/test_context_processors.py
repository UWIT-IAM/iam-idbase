from idbase.context_processors import settings_context


def test_settings_context_defaults(settings):
    delattr(settings, 'SETTINGS_CONTEXT_ATTRIBUTES')
    settings.DEBUG = False
    settings.LOGOUT_URL = '/flogout'
    settings.HOME_URL = '/home/'
    assert settings_context(None) == {
        'settings': dict(HOME_URL='/home/', LOGOUT_URL='/flogout',
                         DEBUG=False)}


def test_settings_context_attributes(settings):
    settings.SETTINGS_CONTEXT_ATTRIBUTES = ['A', 'B', 'C']
    settings.A = 1
    settings.B = '2'
    assert settings_context(None) == {'settings': dict(A=1, B='2', C=None)}
