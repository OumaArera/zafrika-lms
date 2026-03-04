from rest_framework import serializers
from ..models import Subject, SubjectTag


class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subject
        fields = ["id", "name", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


# ---------- WRITE SERIALIZER ----------

class SubjectTagWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubjectTag
        fields = ["id", "subject", "name"]
        read_only_fields = ["id"]


# ---------- READ SERIALIZER ----------

class SubjectTagReadSerializer(serializers.ModelSerializer):

    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = SubjectTag
        fields = [
            "id",
            "subject",
            "subject_name",
            "name",
            "created_at",
            "updated_at",
        ]