from rest_framework import viewsets
from ..models import ChallengeNote, ChallengeEnrollment
from ..serializers import ChallengeNoteCreateSerializer
from ..utils import validate_day_access


class ChallengeNoteViewSet(viewsets.ModelViewSet):

    queryset = ChallengeNote.objects.select_related(
        "day",
        "enrollment",
        "author_student",
        "author_teacher"
    )
    serializer_class = ChallengeNoteCreateSerializer

    def get_queryset(self):
        user = self.request.user

        if hasattr(user, "student"):
            return self.queryset.filter(
                enrollment__student=user.student
            )

        return self.queryset

    def perform_create(self, serializer):

        day = serializer.validated_data["day"]

        enrollment = ChallengeEnrollment.objects.get(
            student=self.request.user.student,
            challenge=day.challenge
        )

        validate_day_access(enrollment, day.day_number)

        serializer.save(
            enrollment=enrollment,
            author_student=self.request.user.student
        )