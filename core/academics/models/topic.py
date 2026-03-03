import uuid
from django.db import models
from ..models import Subject
from ...accounts.models import Teacher



class Topic(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="topics",
    )

    author = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="topics",
    )

    content = models.TextField()
    video_link = models.URLField(
        max_length=500,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["description"]),
            models.Index(fields=["subject"]),
            models.Index(fields=["author"]),
        ]

    def __str__(self):
        return self.title