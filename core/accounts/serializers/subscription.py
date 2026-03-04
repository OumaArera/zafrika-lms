from rest_framework import serializers
from ..models import Subscription
from ..serializers import StudentNestedSerializer, VirtualClassReadSerializer
from ...academics.serializers import SubjectNestedSerializer, TopicNestedSerializer

class SubscriptionSerializer(serializers.ModelSerializer):

    student = StudentNestedSerializer(read_only=True)
    subjects = SubjectNestedSerializer(many=True, read_only=True)
    topics = TopicNestedSerializer(many=True, read_only=True)
    virtual_classes = VirtualClassReadSerializer(many=True, read_only=True)

    class Meta:
        model = Subscription
        fields = [
            "id",
            "student",
            "tier",
            "duration",
            "start_date",
            "end_date",
            "active",
            "notes_access",
            "exercises_access",
            "exams_access",
            "virtual_classes_access",
            "subjects",
            "topics",
            "virtual_classes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "student", "start_date", "end_date", "created_at", "updated_at"]