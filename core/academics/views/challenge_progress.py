from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from ..models import *
from ..serializers import ChallengeDayProgressSerializer

class ChallengeDayProgressViewSet(viewsets.ModelViewSet):
    queryset = ChallengeDayProgress.objects.select_related(
        "enrollment",
        "day",
        "enrollment__student",
        "day__challenge"
    )
    serializer_class = ChallengeDayProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Students only see their own progress
        if hasattr(user, "student_profile"):
            return self.queryset.filter(enrollment__student=user.student_profile)
        # Teachers/admins can see all progress
        return self.queryset

    def perform_create(self, serializer):
        user = self.request.user
        day = serializer.validated_data["day"]

        # Ensure the user owns the enrollment
        try:
            enrollment = day.challenge.enrollments.get(student=user.student_profile)
        except ChallengeEnrollment.DoesNotExist:
            raise PermissionDenied("You are not enrolled in this challenge.")

        serializer.save(enrollment=enrollment)