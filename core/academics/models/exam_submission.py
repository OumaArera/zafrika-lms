import uuid
from django.db import models


class ExamSubmission(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    student = models.ForeignKey(
        "accounts.Student",
        on_delete=models.CASCADE,
        related_name="exam_submissions",
    )

    exam = models.ForeignKey(
        "academics.ExamQuestion",
        on_delete=models.CASCADE,
        related_name="submissions",
    )

    text_content = models.TextField(blank=True, null=True)

    supervisor = models.ForeignKey(
        "accounts.Teacher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="exam_supervisions",
    )

    is_marked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["student"]),
            models.Index(fields=["exam"]),
            models.Index(fields=["supervisor"]),
            models.Index(fields=["is_marked"]),
        ]

    def __str__(self):
        return f"{self.student} - {self.exam}"