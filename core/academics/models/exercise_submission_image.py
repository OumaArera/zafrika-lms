import uuid
from django.db import models


class SubmissionImage(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    submission = models.ForeignKey(
        "academics.ExerciseSubmission",
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(upload_to="media/exercise_submissions/")

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["uploaded_at"]