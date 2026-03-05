import uuid
from django.db import models
from django.conf import settings
from .parent import Parent

class Student(models.Model):

    class SEX(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )

    parent = models.ForeignKey(
        Parent,
        on_delete=models.SET_NULL,
        related_name="students",
        blank=True, 
        null=True
    )

    admission_number = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    middle_names = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    sex = models.CharField(max_length=10, choices=SEX.choices)
    date_of_birth = models.DateField()
    school_name = models.CharField(max_length=255)
    county = models.CharField(max_length=100)
    subjects_enrolled = models.ManyToManyField(
        "academics.Subject",
        through="academics.StudentSubject",
        related_name="student_subject"
    )
    current_school_level = models.CharField(max_length=100)
    parental_consent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["county", "current_school_level"]),
            models.Index(fields=["last_name", "first_name"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"