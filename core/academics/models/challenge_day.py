import uuid
from django.db import models
from .challenge import Challenge

class ChallengeDay(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name="days"
    )

    day_number = models.PositiveIntegerField()

    title = models.CharField(max_length=255)
    description = models.TextField()
    content = models.TextField()

    class Meta:
        unique_together = ("challenge", "day_number")
        ordering = ["day_number"]

    def __str__(self):
        return f"{self.challenge.title} - Day {self.day_number}"