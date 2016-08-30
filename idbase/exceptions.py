class BadRequestError(Exception):
    "Exception to raise for invalid user input. Corresponds to a 400 error."


class InvalidSessionError(Exception):
    """
    Exception to raise for authentication failures, session expirations, or
    invalid session state. Corresponds to a 401 error and a login invalid
    or session invalid/timeout message.
    """


class NotFoundError(Exception):
    """Corresponds to a 404 error and is currently unused."""


class ServiceError(Exception):
    """
    Exception to raise for unrecoverable errors. Generally corresponds to a
    500 error and a "call the service center" message.
    """


class LoginNotPerson(Exception):
    """Exception to raise on login for non-personal netids."""
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args)
        self.netid = kwargs.pop('netid', None)
