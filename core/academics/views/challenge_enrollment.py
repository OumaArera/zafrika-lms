from rest_framework import viewsets
from rest_framework.response import Response
from django.utils.timezone import now
from rest_framework.decorators import action
from ..models import *
from ..serializers import *
from ..utils import get_current_day


class ChallengeEnrollmentViewSet(viewsets.ModelViewSet):

    queryset = ChallengeEnrollment.objects.select_related(
        "challenge",
        "student"
    ).prefetch_related(
        "progress"
    )

    def get_queryset(self):
        user = self.request.user

        if hasattr(user, "student_profile"):
            return self.queryset.filter(student=user.student_profile)

        return self.queryset

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ChallengeEnrollmentCreateSerializer
        return ChallengeEnrollmentSerializer

    def perform_create(self, serializer):
        serializer.save(
            student=self.request.user.student_profile,
            status="pending"
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        enrollment = self.get_object()

        enrollment.status = "approved"
        enrollment.start_date = now().date()
        enrollment.current_day = 1
        enrollment.save()

        return Response({"status": "approved"})

    @action(detail=True, methods=["get"])
    def progress(self, request, pk=None):
        enrollment = self.get_object()

        current_day = get_current_day(enrollment)

        completed_days = ChallengeDayProgress.objects.filter(
            enrollment=enrollment,
            is_completed=True
        ).count()

        total_days = enrollment.challenge.duration_days

        percentage = (completed_days / total_days) * 100

        return Response({
            "current_day": current_day,
            "completed_days": completed_days,
            "total_days": total_days,
            "progress_percentage": percentage
        })