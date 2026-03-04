from rest_framework import serializers
from ..models import TeacherSubject


class TeacherSubjectSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.__str__", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = TeacherSubject
        fields = [
            "id",
            "teacher",
            "teacher_name",
            "subject",
            "subject_name",
            "is_active",
            "assigned_at",
        ]
        read_only_fields = ["id", "teacher_name", "subject_name", "assigned_at"]