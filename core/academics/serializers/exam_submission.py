from rest_framework import serializers
from django.db import transaction
from ..models import ExamSubmission, ExamSubmissionImage
from .exam_submission_image import ExamSubmissionImageSerializer
from .exam_result import ExamResultReadSerializer


class ExamSubmissionCreateSerializer(serializers.ModelSerializer):

    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = ExamSubmission
        fields = [
            "id",
            "student",
            "exam",
            "text_content",
            "supervisor",
            "images",
            "is_marked",
        ]
        read_only_fields = ["id", "is_marked"]

    def validate_images(self, value):
        if len(value) > 10:
            raise serializers.ValidationError(
                "Maximum of 10 images allowed."
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        images = validated_data.pop("images", [])

        submission = ExamSubmission.objects.create(**validated_data)

        image_objects = [
            ExamSubmissionImage(submission=submission, image=image)
            for image in images
        ]

        ExamSubmissionImage.objects.bulk_create(image_objects)

        return submission
    
    
class ExamSubmissionReadSerializer(serializers.ModelSerializer):

    images = ExamSubmissionImageSerializer(many=True, read_only=True)
    result = ExamResultReadSerializer(read_only=True)
    percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = ExamSubmission
        fields = [
            "id",
            "student",
            "exam",
            "text_content",
            "supervisor",
            "is_marked",
            "images",
            "result",
            "percentage",
            "created_at",
            "updated_at",
        ]


