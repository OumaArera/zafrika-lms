import uuid
from django.db import models
from ..models import Subject
from ...accounts.models import *


class TeacherSubject(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="teacher_subjects"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="teacher_subjects"
    )

    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("teacher", "subject")
        indexes = [
            models.Index(fields=["teacher", "subject"]),
        ]
        ordering = ["-assigned_at"]

    def __str__(self):
        return f"{self.teacher.first_name} {self.teacher.last_name} - {self.subject.name}"