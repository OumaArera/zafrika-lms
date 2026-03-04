from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class AuthService:

    @staticmethod
    def login(username: str, password: str):
        user = authenticate(username=username, password=password)
        if not user:
            raise ValueError("Invalid credentials.")

        if user.status != User.Status.ACTIVE:
            raise ValueError("User account is not active.")

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    @staticmethod
    @transaction.atomic
    def create_admin(data):
        user = User.objects.create_superuser(
            username=data["username"],
            phone_number=data["phone_number"],
            password=data["password"],
            email=data.get("email"),
            role=User.Role.ADMIN,
            is_verified=True,
        )
        return user

    @staticmethod
    def block_user(user_id):
        user = User.objects.select_for_update().get(id=user_id)
        user.status = User.Status.BLOCKED
        user.save(update_fields=["status", "updated_at"])
        return user

    @staticmethod
    def unblock_user(user_id):
        user = User.objects.select_for_update().get(id=user_id)
        user.status = User.Status.ACTIVE
        user.save(update_fields=["status", "updated_at"])
        return user

    @staticmethod
    def change_password(user, old_password, new_password):
        if not user.check_password(old_password):
            raise ValueError("Old password incorrect.")

        user.set_password(new_password)
        user.must_change_password = False
        user.save(update_fields=["password", "must_change_password"])
        return user

    @staticmethod
    def reset_student_password(student):
        dob = student.date_of_birth
        new_password = dob.strftime("%d%m%Y")

        user = student.user
        user.set_password(new_password)
        user.must_change_password = True
        user.save(update_fields=["password", "must_change_password"])

        return user