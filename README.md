[![Build Status](https://travis-ci.org/UWIT-IAM/iam-idbase.svg?branch=master)](https://travis-ci.org/UWIT-IAM/iam-idbase)
[![Coverage Status](https://coveralls.io/repos/github/UWIT-IAM/iam-idbase/badge.svg?branch=master)](https://coveralls.io/github/UWIT-IAM/iam-idbase?branch=master)


# iam-idbase
A base look-and-feel package for apps designed to run on Identity.UW with django.

## What it includes:
* template idbase/base.html and the common site-wide statics for dependent apps to include.
* Angular app in identity.js for common site-wide behaviors.
* middleware login_url_middleware and session_timeout_middleware for managing logins and sessions in a common way.
* RESTDispatch class for creating new api endpoints.
* settings_context context_processor for exposing settings to templates.

## Using it within a project
* Add 'compressor' and 'idbase' to your settings.INSTALLED_APPS
* Add 'idbase.middleware.session_timeout_middleware' to settings.MIDDLEWARE after SessionMiddleware and set SESSION_EXPIRE_AT_BROWSER_CLOSE to True.
* Replace any authentication middleware in settings.MIDDLEWARE with 'idbase.middleware.login_url_middleware'.
* Add 'idbase.context_processors.settings_context' to your settings.TEMPLATES list of context_processors.
* Declare a settings.LOGIN_URL and a settings.LOGOUT_URL
* Declare the settings you want exposed to your templates...
```
# settings.py

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
INSTALLED_APPS = (
     ...
     'compressor',
     'idbase',
     ...)

MIDDLEWARE = [
    ...
    'idbase.middleware.session_timeout_middleware',
    'idbase.middleware.login_url_middleware,
    ...
]
IDBASE_IRWS_CLASS = 'yourapp.dao.IRWS'

SETTINGS_CONTEXT_ATTRIBUTES = ['DEBUG', 'LOGOUT_URL', 'HOME_URL']

TEMPLATES = [
    {
        ...
        'OPTIONS': {
            'context_processors': [
                ...
                'idbase.context_processors.settings_context'
            ]}}]
COMPRESS_ENABLED = True
STATIC_URL = '/static-yourapp/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static-yourapp')
STATICFILES_FINDERS = (
    ...
    'compressor.finders.CompressorFinder',
)
```
* Add some urls to handle login, logout, and loginstatus...
```
# urls.py

from idbase.views import login, logout
from idbase.api import LoginStatus

urlpatterns = [
    url(r'^login/$', login),
    url(r'^logout/$', logout),
    url(r'^api/loginstatus$', LoginStatus().run),
    ...
]
```
* Extend idbase/base.html in your templates...
```
{% extends "idbase/base.html" %}

{% block js %}
  {{block.super}}
  <link rel="stylesheet" href="{% static "css/more.css" %}">
{% endblock %}

{% block css %}
  {{block.super}}
  <script src="{% static "js/more.js" %}"></script>
{% endblock %}

{% block content %}
<h1>Set up your account</h1>
...
{% endblock %}
```

## Deploying
Add 'collectstatic' and 'compress' tasks to your deploy playbook.
```
  - name: collect {{app_name}} statics
    django_manage:
      command: collectstatic --noinput
      app_path: "{{target_static_path}}"
      python_path: "{{python_path}}"
      virtualenv: "{{your_virtualenv}}"

  - name: compress {{app_name}} statics
    django_manage:
      command: compress --force
      app_path: "{{target_static_path}}"
      python_path: "{{python_path}}"
      virtualenv: "{{your_virtualenv}}"
```
