import uuid
from django.db import models
from django.utils import timezone
from ...academics.models import Subject, Topic
from ..models import VirtualClass, Student


class Subscription(models.Model):

    class Tier(models.TextChoices):
        FULL = "full", "Full Access"
        PARTIAL = "partial", "Partial Access"

    class Duration(models.TextChoices):
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        ANNUAL = "annual", "Annual"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )
    tier = models.CharField(max_length=20, choices=Tier.choices)
    duration = models.CharField(max_length=20, choices=Duration.choices)
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField(blank=True, null=True)
    active = models.BooleanField(default=True)

    # Access control flags
    notes_access = models.BooleanField(default=True)
    exercises_access = models.BooleanField(default=True)
    exams_access = models.BooleanField(default=True)
    virtual_classes_access = models.BooleanField(default=True)

    # Optional: fine-grained access
    subjects = models.ManyToManyField(Subject, blank=True, related_name="subscriptions")
    topics = models.ManyToManyField(Topic, blank=True, related_name="subscriptions")
    virtual_classes = models.ManyToManyField(VirtualClass, blank=True, related_name="subscriptions")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["student", "active"]),
            models.Index(fields=["start_date", "end_date"]),
        ]

    def save(self, *args, **kwargs):
        # Automatically compute end_date based on duration
        if not self.end_date:
            if self.duration == self.Duration.WEEKLY:
                self.end_date = self.start_date + timezone.timedelta(weeks=1)
            elif self.duration == self.Duration.MONTHLY:
                self.end_date = self.start_date + timezone.timedelta(days=30)
            elif self.duration == self.Duration.ANNUAL:
                self.end_date = self.start_date + timezone.timedelta(days=365)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.first_name} - {self.tier} ({self.duration})"