from rest_framework import serializers
from django.db import transaction
from ..models import Group, Student
from .nested import StudentNestedSerializer


class GroupCreateUpdateSerializer(serializers.ModelSerializer):

    student_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )

    students = StudentNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = [
            "id",
            "name",
            "description",
            "student_ids",
            "students",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "students", "created_at", "updated_at"]

    def validate_student_ids(self, value):
        existing = Student.objects.filter(id__in=value).count()
        if existing != len(value):
            raise serializers.ValidationError("One or more students not found.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        student_ids = validated_data.pop("student_ids", [])
        group = Group.objects.create(**validated_data)
        if student_ids:
            group.students.set(student_ids)
        return group

    @transaction.atomic
    def update(self, instance, validated_data):
        student_ids = validated_data.pop("student_ids", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if student_ids is not None:
            instance.students.set(student_ids)

        return instance

