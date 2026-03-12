import uuid
from django.db import models


class SubscriptionPlan(models.Model):

    class Tier(models.TextChoices):
        FULL = "full", "Full Access"
        PARTIAL = "partial", "Partial Access"

    class Duration(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        ANNUAL = "annual", "Annual"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=150)

    tier = models.CharField(max_length=20, choices=Tier.choices)

    duration = models.CharField(max_length=20, choices=Duration.choices)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    currency = models.CharField(max_length=10, default="KES")

    description = models.TextField(blank=True, null=True)

    # Access flags (so the UI can display what the plan includes)
    notes_access = models.BooleanField(default=True)
    exercises_access = models.BooleanField(default=True)
    exams_access = models.BooleanField(default=True)
    virtual_classes_access = models.BooleanField(default=True)
    submit_exam_questions_attempts = models.BooleanField(default=False)
    submit_exercise_attempts = models.BooleanField(default=False)

    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["price"]

    def __str__(self):
        return f"{self.name} - {self.price} {self.currency}"