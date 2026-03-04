from rest_framework import serializers
from ..models import SubjectTag


class SubjectTagNestedSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = SubjectTag
        fields = [
            "id",
            "subject_name",
            "name",
            "created_at",
        ]