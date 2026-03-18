import uuid
from django.db import models
from .challenge_enrollment import ChallengeEnrollment
from .challenge_day import ChallengeDay


class ChallengeDayProgress(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    enrollment = models.ForeignKey(
        ChallengeEnrollment,
        on_delete=models.CASCADE,
        related_name="progress"
    )

    day = models.ForeignKey(
        ChallengeDay,
        on_delete=models.CASCADE,
        related_name="progress_entries"
    )

    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("enrollment", "day")