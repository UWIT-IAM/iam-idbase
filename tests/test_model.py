from idbase.models import LoginUrlRemoteUser


def test_login_url_remote_user_no_auth():
    user = LoginUrlRemoteUser()
    assert not user.is_authenticated()


def test_login_url_remote_user_basic():
    user = LoginUrlRemoteUser(remote_user='foo@washington.edu')
    assert user.is_authenticated()
    assert user.get_username() == 'foo@washington.edu'
    assert user.netid == 'foo'
    assert user.get_full_name() is None


def test_login_url_remote_with_name():
    user = LoginUrlRemoteUser(remote_user='foo@washington.edu',
                              full_name='Foo')
    assert user.get_full_name() == 'Foo'
