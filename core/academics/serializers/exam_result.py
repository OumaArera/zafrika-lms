from rest_framework import serializers
from django.db import transaction
from ..models import ExamResult


class ExamResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExamResult
        fields = [
            "id",
            "exam_submission",
            "score",
            "out_of",
            "comments",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, data):
        if data["score"] > data["out_of"]:
            raise serializers.ValidationError(
                "Score cannot be greater than out_of."
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        submission = validated_data["exam_submission"]

        if hasattr(submission, "result"):
            raise serializers.ValidationError(
                "This exam submission has already been graded."
            )

        result = ExamResult.objects.create(**validated_data)

        submission.is_marked = True
        submission.save(update_fields=["is_marked"])

        return result



class ExamResultReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExamResult
        fields = [
            "id",
            "score",
            "out_of",
            "comments",
            "created_at",
        ]