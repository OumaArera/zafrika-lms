from rest_framework import serializers
from ..models import Parent


class ParentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Parent
        fields = [
            "id",
            "first_name",
            "last_name",
            "id_number",
            "phone_number",
            "email",
            "date_of_birth",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]