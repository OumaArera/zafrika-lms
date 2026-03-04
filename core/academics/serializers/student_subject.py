from rest_framework import serializers
from ..models import StudentSubject

class StudentSubjectSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = StudentSubject
        fields = [
            "id",
            "student",
            "student_name",
            "subject",
            "subject_name",
            "is_active",
            "assigned_at",
        ]
        read_only_fields = ["id", "student_name", "subject_name", "assigned_at"]