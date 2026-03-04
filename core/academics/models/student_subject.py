import uuid
from django.db import models
from ...accounts.models import Student
from .subject import Subject


class StudentSubject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="subjects"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="students"
    )
    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "subject")
        indexes = [
            models.Index(fields=["student", "subject"]),
        ]

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.subject.name}"