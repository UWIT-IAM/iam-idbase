from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from idbase.views import login
from idbase.api import LoginStatus

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^secure', login_required(views.index), name='secure'),
    url(r'^login$', login),
    url(r'^api/loginstatus$', LoginStatus().run),
]
