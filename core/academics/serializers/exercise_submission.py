from rest_framework import serializers
from django.db import transaction
from ..models import ExerciseSubmission, SubmissionImage
from .submission_image import SubmissionImageSerializer


class ExerciseSubmissionCreateSerializer(serializers.ModelSerializer):

    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = ExerciseSubmission
        fields = [
            "id",
            "student",
            "exercise",
            "text_content",
            "supervisor",
            "images",
            "supervisor_comment",
            "is_marked"
        ]
        read_only_fields = ["id"]

    def validate_images(self, value):
        if len(value) > 5:
            raise serializers.ValidationError(
                "Maximum of 5 images allowed."
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        images = validated_data.pop("images", [])

        submission = ExerciseSubmission.objects.create(**validated_data)

        image_objects = [
            SubmissionImage(submission=submission, image=image)
            for image in images
        ]

        SubmissionImage.objects.bulk_create(image_objects)

        return submission
    
class ExerciseSubmissionReadSerializer(serializers.ModelSerializer):

    images = SubmissionImageSerializer(many=True, read_only=True)

    class Meta:
        model = ExerciseSubmission
        fields = [
            "id",
            "student",
            "exercise",
            "text_content",
            "supervisor",
            "images",
            "supervisor_comment",
            "is_marked",
            "created_at",
            "updated_at",
        ]