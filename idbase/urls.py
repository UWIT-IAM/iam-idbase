from django.conf.urls import url
from idbase.decorators import uw_login_required
from idbase.views import login, logout
from idbase.api import LoginStatus

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^secure', uw_login_required(views.index), name='secure'),
    url(r'^(?P<template>nonav)/$', views.index, name='nonav'),
    url(r'^login/$', login),
    url(r'^logout/$', logout),
    url(r'^api/loginstatus$', LoginStatus().run),
]
