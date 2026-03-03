from rest_framework import serializers
from ..models import Topic
from ...accounts.serializers import SubjectNestedSerializer
from .teacher_nested import TeacherNestedSerializer  
from .exercise import ExerciseNestedSerializer


class TopicCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Topic
        fields = [
            "id",
            "title",
            "description",
            "subject",
            "author",
            "content",
            "video_link",
        ]
        read_only_fields = ["id"]


class TopicReadSerializer(serializers.ModelSerializer):

    subject = SubjectNestedSerializer(read_only=True)
    author = TeacherNestedSerializer(read_only=True)
    exercises = ExerciseNestedSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Topic
        fields = [
            "id",
            "title",
            "description",
            "subject",
            "author",
            "content",
            "video_link",
            "exercises",
            "created_at",
            "updated_at",
        ]