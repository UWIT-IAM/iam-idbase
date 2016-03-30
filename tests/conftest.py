import os
from pytest import fixture
from importlib import import_module

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'idbase_site.settings')


@fixture
def session():
    engine = import_module('django.contrib.sessions.backends.signed_cookies')
    store = engine.SessionStore()
    store['active'] = True  # set something so we can check if it's cleared.
    store.modified = False
    return store
