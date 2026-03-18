from rest_framework import serializers
from ..models import *


class ChallengeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Challenge
        fields = "__all__"


class ChallengeDaySerializer(serializers.ModelSerializer):

    class Meta:
        model = ChallengeDay
        fields = "__all__"


class ChallengeEnrollmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChallengeEnrollment
        fields = "__all__"
        read_only_fields = ["status", "start_date", "current_day"]


class ChallengeAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChallengeAssignment
        fields = ["id", "title", "day", "description"]
        read_only_fields = ["id"]


class ChallengeNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChallengeNote
        fields = [
            "id",
            "text_content",
            "youtube_link",
            "created_at",
        ]


class ChallengeDayCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChallengeDay
        fields = [
            "id",
            "challenge",
            "day_number",
            "title",
            "description",
            "content",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        """
        Ensure the day_number is unique per challenge
        """
        challenge = attrs.get("challenge")
        day_number = attrs.get("day_number")
        if ChallengeDay.objects.filter(challenge=challenge, day_number=day_number).exists():
            raise serializers.ValidationError(f"Day {day_number} already exists for this challenge")
        return attrs


class ChallengeDayReadSerializer(serializers.ModelSerializer):
    assignments = ChallengeAssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = ChallengeDay
        fields = [
            "id",
            "day_number",
            "title",
            "description",
            "content",
            "assignments",
        ]

class ChallengeDetailSerializer(serializers.ModelSerializer):

    days = ChallengeDayReadSerializer(many=True, read_only=True)

    class Meta:
        model = Challenge
        fields = [
            "id",
            "title",
            "description",
            "duration_days",
            "days"
        ]


class ChallengeDayProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChallengeDayProgress
        fields = [
            "id",
            "enrollment",
            "day",
            "is_completed",
            "completed_at",
        ]
        read_only_fields = ["id", "completed_at", "enrollment"]

    def update(self, instance, validated_data):
        """
        Override update to mark day as completed and update enrollment's current_day.
        """
        if validated_data.get("is_completed", False) and not instance.is_completed:
            instance.is_completed = True
            from django.utils.timezone import now
            instance.completed_at = now()
            instance.save()

            # Update current day of the enrollment if needed
            enrollment = instance.enrollment
            next_day_number = instance.day.day_number + 1
            if next_day_number > enrollment.current_day:
                enrollment.current_day = next_day_number
                enrollment.save()

        return instance 
    

class ChallengeEnrollmentSerializer(serializers.ModelSerializer):
    challenge = ChallengeDetailSerializer(read_only=True)
    class Meta:
        model = ChallengeEnrollment
        fields = [
            "id",
            "challenge",
            "status",
            "start_date",
            "current_day",
            "created_at",
        ]
        read_only_fields = ["status", "start_date", "current_day"]


class ChallengeEnrollmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChallengeEnrollment
        fields = [
            "id",
            "challenge",
            "status",
            "start_date",
            "current_day",
            "created_at",
        ]
        read_only_fields = ["status", "start_date", "current_day"]


class ChallengeSubmissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChallengeSubmission
        fields = [
            "id",
            "assignment",
            "text_content",
            "submitted_at",
        ]
        read_only_fields = ["submitted_at"]


class ChallengeNoteCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChallengeNote
        fields = [
            "id",
            "day",
            "text_content",
            "youtube_link",
        ]

class ChallengeCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Challenge
        fields = [
            "id",
            "title",
            "description",
            "subject",
            "duration_days",
            "is_active",
        ]
        read_only_fields = ["id"]

class ChallengeProgressSerializer(serializers.Serializer):
    current_day = serializers.IntegerField()
    completed_days = serializers.IntegerField()
    total_days = serializers.IntegerField()
    progress_percentage = serializers.FloatField()