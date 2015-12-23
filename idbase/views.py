from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings


# Identity home page
def index(request, template=None):

    #person = PersonDAO(request.session, netid=netid)
    conf = {'urls': settings.CORE_URLS,
            'logged_in_person': {'netid': 'foo', 'banner_netid': 'foo2', 'name': 'FooMan'},
            'is_debug': settings.DEBUG}

    return render(request, 'idbase/index.html', conf)
