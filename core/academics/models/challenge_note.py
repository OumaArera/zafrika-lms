import uuid
from django.db import models
from .challenge_enrollment import ChallengeEnrollment
from .challenge_day import ChallengeDay
from ...accounts.models import Teacher, Student


class ChallengeNote(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    day = models.ForeignKey(
        ChallengeDay,
        on_delete=models.CASCADE,
        related_name="notes"
    )

    enrollment = models.ForeignKey(
        ChallengeEnrollment,
        on_delete=models.CASCADE,
        related_name="notes",
        null=True,
        blank=True
    )

    author_teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    author_student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    text_content = models.TextField()
    youtube_link = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)