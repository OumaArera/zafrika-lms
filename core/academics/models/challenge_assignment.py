import uuid
from django.db import models
from .challenge_day import ChallengeDay


class ChallengeAssignment(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    day = models.ForeignKey(
        ChallengeDay,
        on_delete=models.CASCADE,
        related_name="assignments"
    )

    title = models.CharField(max_length=255)
    description = models.TextField()