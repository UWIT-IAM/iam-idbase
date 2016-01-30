from django.contrib.auth.middleware import PersistentRemoteUserMiddleware
from django.conf import settings


class LoginMiddleware(PersistentRemoteUserMiddleware):
    def process_request(self, request):
        if request.path == settings.LOGIN_URL and request.META.get('REMOTE_USER', '').endswith('@washington.edu'):
            request.session.flush()
            super(LoginMiddleware, self).process_request(request)
