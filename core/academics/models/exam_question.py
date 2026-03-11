import uuid
from django.db import models


class ExamQuestion(models.Model):

    class GradeChoices(models.TextChoices):
        GRADE_1 = "grade_1", "Grade 1"
        GRADE_2 = "grade_2", "Grade 2"
        GRADE_3 = "grade_3", "Grade 3"
        GRADE_4 = "grade_4", "Grade 4"
        GRADE_5 = "grade_5", "Grade 5"
        GRADE_6 = "grade_6", "Grade 6"
        GRADE_7 = "grade_7", "Grade 7"
        GRADE_8 = "grade_8", "Grade 8"
        GRADE_9 = "grade_9", "Grade 9"
        GRADE_10 = "grade_10", "Grade 10"
        GRADE_11 = "grade_11", "Grade 11"
        GRADE_12 = "grade_12", "Grade 12"
        FORM_3 = "form_3", "Form 3"
        FORM_4 = "form_4", "Form 4"

    class LevelChoices(models.TextChoices):
        SCOUT = "scout", "Scout"
        EXPLORER = "explorer", "Explorer"
        LEGEND = "legend", "Legend"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=255)

    instructions = models.TextField()
    content = models.TextField()

    subject_tag = models.ForeignKey(
        "academics.SubjectTag",
        on_delete=models.CASCADE,
        related_name="exam_questions",
    )

    video_link = models.URLField(
        max_length=500,
        blank=True,
        null=True,
    )

    grade = models.CharField(
        max_length=20,
        choices=GradeChoices.choices,
    )

    level = models.CharField(
        max_length=20,
        choices=LevelChoices.choices,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["grade"]),
            models.Index(fields=["level"]),
            models.Index(fields=["subject_tag"]),
        ]

    def __str__(self):
        return self.title
