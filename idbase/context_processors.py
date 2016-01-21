from django.conf import settings


def app_context(request):
    # Set some sensible defaults
    app = {'base_url': '/', 'css_loads': [], 'javascript_loads': []}

    app_contexts = getattr(settings, 'APP_CONTEXTS', {})

    if request.resolver_match.namespace in app_contexts:
        app.update(app_contexts[request.resolver_match.namespace])
    elif 'default' in app_contexts:
        app.update(app_contexts['default'])

    return {'app': app}
