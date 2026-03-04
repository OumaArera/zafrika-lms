from rest_framework import serializers
from ..models import Student, Group


class StudentNestedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = [
            "id",
            "admission_number",
            "first_name",
            "last_name",
            "current_school_level",
        ]


class GroupNestedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = [
            "id",
            "name",
            "description",
        ]