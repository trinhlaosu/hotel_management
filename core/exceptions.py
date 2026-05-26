"""DRF exception formatting."""
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None and isinstance(response.data, dict):
        detail = response.data.get('detail')
        if detail is not None:
            response.data = {'error': str(detail)}
        elif 'error' not in response.data:
            field, errors = next(iter(response.data.items()))
            if isinstance(errors, (list, tuple)) and errors:
                message = errors[0]
            else:
                message = errors
            response.data = {'error': f'{field}: {message}'}
    return response
