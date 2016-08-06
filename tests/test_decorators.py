from idbase.decorators import uw_login_required
from idbase.models import UwUser


def test_uw_login_required(rf):
    """
    Make sure our UwUser is handled correctly uw_login_required. We used to use
    request.user and django.contrib.auth.decorators.login_required, however
    our custom User model fell out of line with django's in Django 1.10.
    There was no clean way to satisfy pre-1.10 and post-1.10, and it wouldn't
    prevent future breakage, so we divest ourselves of request.user and
    login_required, and use custom request.uw_user and uw_login_required.
    """
    @uw_login_required
    def fake_view(request):
        return 'is_auth'
    req = rf.get('/')
    req.session = {}
    req.uw_user = UwUser()
    response = fake_view(req)
    assert response.status_code == 302
    req.uw_user.is_authenticated = True
    assert fake_view(req) == 'is_auth'
