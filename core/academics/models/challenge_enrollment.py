import uuid
from django.db import models
from ...accounts.models import Student
from .challenge import Challenge


class ChallengeEnrollment(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("completed", "Completed"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="challenge_enrollments"
    )

    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    start_date = models.DateField(null=True, blank=True)

    current_day = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "challenge")

    def __str__(self):
        return f"{self.student} - {self.challenge} ({self.status})"