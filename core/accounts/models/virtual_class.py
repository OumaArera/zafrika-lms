from django.db import models
import uuid


class VirtualClass(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=255)

    url = models.URLField()

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    references = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    groups = models.ManyToManyField(
        "accounts.Group",
        related_name="virtual_classes"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_time"]
        indexes = [
            models.Index(fields=["start_time"]),
        ]

    def __str__(self):
        return self.title