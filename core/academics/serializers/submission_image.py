from rest_framework import serializers
from ..models import SubmissionImage


class SubmissionImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubmissionImage
        fields = ["id", "image", "uploaded_at"]
        read_only_fields = ["id", "uploaded_at"]