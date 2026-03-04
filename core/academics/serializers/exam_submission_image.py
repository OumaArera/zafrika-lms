from rest_framework import serializers
from ..models import ExamSubmissionImage


class ExamSubmissionImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExamSubmissionImage
        fields = ["id", "image", "uploaded_at"]
        read_only_fields = ["id", "uploaded_at"]