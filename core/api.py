"""DRF response helpers."""
from rest_framework import status, viewsets
from rest_framework.response import Response


def api_response(data=None, message='', status=200, error='', pagination=None):
    body = {}
    if message:
        body['message'] = message
    if error:
        body['error'] = error
    if data is not None:
        body['data'] = data
    if pagination is not None:
        body['pagination'] = pagination
    return Response(body, status=status)


def paginated_api_response(view, queryset):
    page = view.paginate_queryset(queryset)
    if page is None:
        return api_response(data=view.serialize_response(queryset, many=True))

    serializer = view.get_response_serializer_class()(page, many=True)
    paginator = view.paginator
    return api_response(
        data=serializer.data,
        pagination={
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
        },
    )


def serializer_error_response(serializer):
    for field, errors in serializer.errors.items():
        if isinstance(errors, (list, tuple)) and errors:
            return api_response(error=f'{field}: {errors[0]}', status=400)
        return api_response(error=f'{field}: {errors}', status=400)
    return api_response(error='Du lieu khong hop le', status=400)


class ApiResponseModelViewSet(viewsets.ModelViewSet):
    """ModelViewSet that keeps the project's response envelope."""

    response_serializer_class = None
    success_messages = {}

    def get_response_serializer_class(self):
        return self.response_serializer_class or self.get_serializer_class()

    def serialize_response(self, instance, many=False):
        serializer_class = self.get_response_serializer_class()
        return serializer_class(instance, many=many).data

    def get_success_message(self, action):
        return self.success_messages.get(action, '')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return paginated_api_response(self, queryset)

    def retrieve(self, request, *args, **kwargs):
        return api_response(data=self.serialize_response(self.get_object()))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return api_response(
            data=self.serialize_response(instance),
            message=self.get_success_message('create'),
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        serializer = self.get_serializer(
            self.get_object(),
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return api_response(
            data=self.serialize_response(instance),
            message=self.get_success_message('update'),
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.serialize_response(instance)
        self.perform_destroy(instance)
        return api_response(
            data=data,
            message=self.get_success_message('destroy'),
        )

    def perform_destroy(self, instance):
        if hasattr(instance, 'is_deleted'):
            instance.is_deleted = True
            instance.save(update_fields=['is_deleted', 'updated_at'])
            return
        super().perform_destroy(instance)
