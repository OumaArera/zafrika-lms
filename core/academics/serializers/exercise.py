from rest_framework import serializers
from ..models import Exercise
from ...accounts.serializers import SubjectNestedSerializer
from .topic_nested import TopicNestedSerializer  


class ExerciseCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Exercise
        fields = [
            "id",
            "title",
            "topic",
            "subject",
            "instructions",
            "content",
            "video_link",
            "level",
        ]
        read_only_fields = ["id"]


class ExerciseReadSerializer(serializers.ModelSerializer):

    topic = TopicNestedSerializer(read_only=True)
    subject = SubjectNestedSerializer(read_only=True)

    class Meta:
        model = Exercise
        fields = [
            "id",
            "title",
            "topic",
            "subject",
            "instructions",
            "content",
            "video_link",
            "level",
            "created_at",
            "updated_at",
        ]

class ExerciseNestedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Exercise
        fields = [
            "id",
            "title",
            "level",
            "video_link",
            "created_at",
        ]
        read_only_fields = fields