from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from ..models import *
from ..serializers import (
    ChallengeDetailSerializer,
    ChallengeCreateSerializer
)


class ChallengeViewSet(viewsets.ModelViewSet):

    queryset = Challenge.objects.select_related(
        "subject",
        "created_by"
    ).prefetch_related(
        "days__assignments"
    )

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ChallengeCreateSerializer
        return ChallengeDetailSerializer

    def perform_create(self, serializer):
        user = self.request.user

        if not hasattr(user, "teacher_profile"):
            raise PermissionDenied("Only teachers can create challenges")

        serializer.save(created_by=user.teacher_profile)