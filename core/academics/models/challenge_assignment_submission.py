import uuid
from django.db import models
from .challenge_assignment import ChallengeAssignment
from .challenge_enrollment import ChallengeEnrollment
from ...accounts.models import Student


class ChallengeSubmission(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    assignment = models.ForeignKey(
        ChallengeAssignment,
        on_delete=models.CASCADE,
        related_name="submissions"
    )

    enrollment = models.ForeignKey(
        ChallengeEnrollment,
        on_delete=models.CASCADE,
        related_name="submissions"
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="challenge_submissions"
    )

    text_content = models.TextField()

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("assignment", "enrollment")