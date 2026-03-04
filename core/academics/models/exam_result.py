import uuid
from django.db import models
from django.core.exceptions import ValidationError


class ExamResult(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    exam_submission = models.OneToOneField(
        "academics.ExamSubmission",
        on_delete=models.CASCADE,
        related_name="result",
    )

    score = models.DecimalField(max_digits=6, decimal_places=2)
    out_of = models.DecimalField(max_digits=6, decimal_places=2)

    comments = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["score"]),
        ]

    def clean(self):
        if self.score > self.out_of:
            raise ValidationError("Score cannot be greater than out_of.")

    def __str__(self):
        return f"Result: {self.score}/{self.out_of}"