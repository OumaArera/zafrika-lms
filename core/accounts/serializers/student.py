from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import get_user_model
from ..models import Student, Parent
from ..utils import generate_admission_number
from .nested_subject import SubjectNestedSerializer
from .nested import GroupNestedSerializer

User = get_user_model()


class StudentCreateSerializer(serializers.ModelSerializer):

    parent_id = serializers.UUIDField(write_only=True)
    phone_number = serializers.CharField(write_only=True)
    subjects = SubjectNestedSerializer(many=True, source='subjects_enrolled', read_only=True)
 

    class Meta:
        model = Student
        fields = [
            "id",
            "parent_id",
            "phone_number",
            "first_name",
            "middle_names",
            "admission_number",
            "last_name",
            "sex",
            "date_of_birth",
            "school_name",
            "county",
            "current_school_level",
            "parental_consent",
            "subjects",
        ]
        read_only_fields = ["id", "admission_number", "subjects",]

    # ---------- FIELD VALIDATION ----------

    def validate_parent_id(self, value):
        if not Parent.objects.filter(id=value).exists():
            raise serializers.ValidationError("Parent not found.")
        return value

    def validate_parental_consent(self, value):
        if not value:
            raise serializers.ValidationError("Parental consent required.")
        return value

    # ---------- ATOMIC CREATION ----------

    @transaction.atomic
    def create(self, validated_data):

        parent_id = validated_data.pop("parent_id")
        phone_number = validated_data.pop("phone_number")

        parent = Parent.objects.select_for_update().get(id=parent_id)

        admission_number = generate_admission_number()

        dob = validated_data["date_of_birth"]
        password = dob.strftime("%d%m%Y")

        user = User.objects.create_user(
            username=admission_number,
            phone_number=phone_number,
            role=User.Role.STUDENT,
            password=password,
            must_change_password=True,
        )

        student = Student.objects.create(
            user=user,
            parent=parent,
            admission_number=admission_number,
            **validated_data,
        )

        return student


class StudentReadSerializer(serializers.ModelSerializer):

    subjects = SubjectNestedSerializer(
        many=True,
        source="subjects_enrolled",
        read_only=True
    )

    groups = GroupNestedSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Student
        fields = [
            "id",
            "admission_number",
            "first_name",
            "middle_names",
            "last_name",
            "sex",
            "date_of_birth",
            "school_name",
            "county",
            "current_school_level",
            "subjects",
            "groups",  
            "created_at",
            "updated_at",
        ]