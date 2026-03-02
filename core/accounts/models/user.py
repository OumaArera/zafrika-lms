import uuid
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)


# ==============================
# USER MANAGER
# ==============================

class UserManager(BaseUserManager):

    def create_user(self, username, phone_number, role, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")

        if not phone_number:
            raise ValueError("Phone number is required")

        if not role:
            raise ValueError("Role is required")

        username = self.model.normalize_username(username)

        email = extra_fields.pop("email", None)
        email = self.normalize_email(email)

        user = self.model(
            username=username,
            phone_number=phone_number,
            role=role,
            email=email,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, phone_number, password=None, **extra_fields):
        extra_fields["role"] = User.Role.ADMIN
        extra_fields["is_staff"] = True
        extra_fields["is_superuser"] = True
        extra_fields["is_verified"] = True

        return self.create_user(
            username=username,
            phone_number=phone_number,
            password=password,
            **extra_fields
        )


# ==============================
# USER MODEL (IDENTITY ONLY)
# ==============================

class User(AbstractBaseUser, PermissionsMixin):

    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        TEACHER = "teacher", "Teacher"
        TEACHER_ADMIN = "teacher-admin", "Teacher Admin"
        ADMIN = "admin", "Admin"
        PARENT = "parent", "Parent"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        BLOCKED = "blocked", "Blocked"
        SUSPENDED = "suspended", "Suspended"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=Role.choices)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    phone_number = models.CharField(max_length=20, unique=True)
    is_verified = models.BooleanField(default=True)
    must_change_password = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["phone_number"]

    class Meta:
        indexes = [
            models.Index(fields=["role", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.username} - {self.role}"