import uuid
from django.db import models
from ...accounts.models import Teacher
from ...academics.models import Subject


class Challenge(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=255)
    description = models.TextField()

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="challenges"
    )

    created_by = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="created_challenges"
    )

    duration_days = models.PositiveIntegerField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title