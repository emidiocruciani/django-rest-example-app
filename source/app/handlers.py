from django.conf import settings
from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler as exception_handler_base


def exception_handler(exc, context):
    response = exception_handler_base(exc, context)
    if response is not None:
        if isinstance(exc, ValidationError):
            message = ValidationError.default_detail
            fields_data = response.data
            if settings.SERIALIZER_VALIDATION_NON_FIELD_ERRORS_KEY in fields_data:
                non_field_messages = fields_data.pop(settings.SERIALIZER_VALIDATION_NON_FIELD_ERRORS_KEY)
                message = '\n'.join(non_field_messages)
            response.data = {'code': 'validation_error', 'message': message, 'fields': fields_data}
        else:
            code = exc.get_codes()
            message = exc.detail
            response.data = {'code': code, 'message': message}
    return response
