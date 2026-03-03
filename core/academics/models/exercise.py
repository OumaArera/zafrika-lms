import uuid
from django.db import models


class Exercise(models.Model):
    class Levels(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        EXPERT = "expert", "Expert"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    topic = models.ForeignKey(
        "academics.Topic",
        on_delete=models.CASCADE,
        related_name="exercises",
    )
    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.CASCADE,
        related_name="exercises",
    )
    instructions = models.TextField()
    content = models.TextField()
    video_link = models.URLField(
        max_length=500,
        blank=True,
        null=True,
    )
    level = models.CharField(
        max_length=20,
        choices=Levels.choices,
        default=Levels.BEGINNER
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["topic"]),
            models.Index(fields=["subject"]),
        ]

    def __str__(self):
        return self.title