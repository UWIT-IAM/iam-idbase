from __future__ import unicode_literals
import re


class LoginUrlRemoteUser(object):
    """
    An implementation of the django User interface that doesn't save to
    or retrieve from a database.
    """

    _is_authenticated = False
    username = ''
    netid = ''
    full_name = None

    def __init__(self, remote_user=None, full_name=None, **kwargs):
        """
        Initialize a user, giving a remote_user if an authenticated user.
        """
        if remote_user:
            self._is_authenticated = True
            self.username = remote_user
            if remote_user and remote_user.endswith('@washington.edu'):
                self.netid = re.sub(r'@washington.edu$', '', remote_user)
            self.full_name = full_name

    def get_username(self):
        return self.username

    def is_authenticated(self):
        return self._is_authenticated

    def get_full_name(self):
        return self.full_name

    def set_full_name(self, full_name):
        self.full_name = full_name
