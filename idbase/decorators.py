from functools import wraps
from django.shortcuts import redirect
from django.conf import settings


def uw_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.uw_user.is_authenticated is True:
            return view_func(request, *args, **kwargs)
        else:
            request.session['_uw_postlogin'] = request.get_full_path()
            return redirect(settings.LOGIN_URL)
    return _wrapped_view
