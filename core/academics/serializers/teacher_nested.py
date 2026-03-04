from rest_framework import serializers
from ...accounts.models import Teacher


class TeacherNestedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Teacher
        fields = ["id", "first_name", "last_name"]