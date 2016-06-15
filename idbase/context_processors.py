from django.conf import settings


def settings_context(request):
    """
    Context processor that exposes settings set by SETTINGS_CONTEXT_ATTRIBUTES.
    """
    default_attributes = ['DEBUG', 'LOGOUT_URL', 'HOME_URL']
    attributes = getattr(settings, 'SETTINGS_CONTEXT_ATTRIBUTES',
                         default_attributes)
    return {'settings': {att: getattr(settings, att, None)
                         for att in attributes}}
