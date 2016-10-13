from functools import wraps
from django.shortcuts import redirect
from django.conf import settings

POSTLOGIN_KEY = '_uw_postlogin'


def uw_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.uwnetid:
            return view_func(request, *args, **kwargs)
        else:
            request.session[POSTLOGIN_KEY] = request.get_full_path()
            return redirect(settings.LOGIN_URL)
    return _wrapped_view
