from rest_framework import viewsets
from ..models import ChallengeSubmission, ChallengeEnrollment
from ..serializers import ChallengeSubmissionSerializer
from ..utils import *


class ChallengeSubmissionViewSet(viewsets.ModelViewSet):

    queryset = ChallengeSubmission.objects.select_related(
        "assignment",
        "enrollment",
        "student"
    )
    serializer_class = ChallengeSubmissionSerializer
    

    def perform_create(self, serializer):

        assignment = serializer.validated_data["assignment"]

        enrollment = ChallengeEnrollment.objects.select_related(
            "challenge"
        ).get(
            student=self.request.user.student_profile,
            challenge=assignment.day.challenge
        )

        validate_day_access(enrollment, assignment.day.day_number)

        serializer.save(
            student=self.request.user.student_profile,
            enrollment=enrollment
        )

        # 🔥 NEW LOGIC
        update_day_progress(enrollment, assignment.day)