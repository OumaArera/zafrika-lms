from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import get_user_model
from ..models import Teacher
from .nested_subject import SubjectNestedSerializer

User = get_user_model()


class TeacherCreateSerializer(serializers.ModelSerializer):

    phone_number = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = Teacher
        fields = [
            "id",
            "phone_number",
            "email",
            "first_name",
            "last_name",
            "sex",
            "county",
            "date_of_birth",
            "tsc_number"
        ]
        read_only_fields = ["id"]

    # ---------- VALIDATION ----------

    def validate_tsc_number(self, value):
        if Teacher.objects.filter(tsc_number=value).exists():
            raise serializers.ValidationError("TSC number already exists.")
        return value

    # ---------- ATOMIC CREATION ----------

    @transaction.atomic
    def create(self, validated_data):

        phone_number = validated_data.pop("phone_number")
        email = validated_data.pop("email", None)

        tsc_number = validated_data["tsc_number"]


        user = User.objects.create_user(
            username=email,
            phone_number=phone_number,
            email=email,
            role=User.Role.TEACHER,
            password=tsc_number,
            must_change_password=True,
        )

        teacher = Teacher.objects.create(
            user=user,
            **validated_data,
        )

        return teacher
    


class TeacherReadSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source="user.username", read_only=True)
    phone_number = serializers.CharField(source="user.phone_number", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    subjects = SubjectNestedSerializer(
        many=True, read_only=True
    )
    class Meta:
        model = Teacher
        fields = [
            "id",
            "username",
            "phone_number",
            "email",
            "first_name",
            "last_name",
            "sex",
            "county",
            "date_of_birth",
            "tsc_number",
            "subjects",
            "created_at",
        ]