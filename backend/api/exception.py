from rest_framework.views import exception_handler


ERROR_MESSAGES = {400: 'Validation Failed', 404: 'Item not found'}


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        status_code = response.status_code
        custom_data = {
            'code': status_code,
            'message': ERROR_MESSAGES.get(
                status_code, response.data.get('detail'))
        }
        response.data = custom_data
    return response
