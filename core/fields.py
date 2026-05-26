"""Custom serializer fields used across the API."""
from rest_framework import serializers
from rest_framework.exceptions import NotFound


class NotFoundPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """Primary-key relation field that returns 404 when the object is missing."""

    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError as exc:
            codes = exc.get_codes()
            if codes == ['does_not_exist'] or codes == 'does_not_exist':
                raise NotFound(str(exc.detail[0]))
            raise
