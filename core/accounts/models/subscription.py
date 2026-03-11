import uuid
from django.db import models
from django.utils import timezone
from ..models import Student
from .subscription_plan import SubscriptionPlan


class Subscription(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )

    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name="subscriptions",
        null=True,
        blank=True
    )

    start_date = models.DateField(default=timezone.localdate)

    end_date = models.DateField(blank=True, null=True)

    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["student", "active"]),
            models.Index(fields=["start_date", "end_date"]),
        ]
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):

        if not self.end_date:
            if self.plan.duration == "daily":
                self.end_date = self.start_date + timezone.timedelta(days=1)

            elif self.plan.duration == "weekly":
                self.end_date = self.start_date + timezone.timedelta(weeks=1)

            elif self.plan.duration == "monthly":
                self.end_date = self.start_date + timezone.timedelta(days=30)

            elif self.plan.duration == "annual":
                self.end_date = self.start_date + timezone.timedelta(days=365)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.first_name} - {self.plan.name}"