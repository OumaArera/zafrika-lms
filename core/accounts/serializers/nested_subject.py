from rest_framework import serializers
from ...academics.models import Subject

class SubjectNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "name"]