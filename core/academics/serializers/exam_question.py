from rest_framework import serializers
from ..models import ExamQuestion
from .subject_tag_nested import SubjectTagNestedSerializer


class ExamQuestionCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExamQuestion
        fields = [
            "id",
            "title",
            "instructions",
            "content",
            "subject_tag",
            "video_link",
            "grade",
            "level",
        ]
        read_only_fields = ["id"]




class ExamQuestionReadSerializer(serializers.ModelSerializer):

    subject_tag = SubjectTagNestedSerializer(read_only=True)

    class Meta:
        model = ExamQuestion
        fields = [
            "id",
            "title",
            "instructions",
            "content",
            "subject_tag",
            "video_link",
            "grade",
            "level",
            "created_at",
            "updated_at",
        ]