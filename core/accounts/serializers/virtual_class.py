from rest_framework import serializers
from django.db import transaction
from ..models import VirtualClass, Group
from .nested import GroupNestedSerializer


class VirtualClassCreateUpdateSerializer(serializers.ModelSerializer):

    group_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )

    class Meta:
        model = VirtualClass
        fields = [
            "id",
            "title",
            "url",
            "start_time",
            "end_time",
            "references",
            "notes",
            "group_ids",
        ]
        read_only_fields = ["id"]

    def validate_group_ids(self, value):
        if not Group.objects.filter(id__in=value).count() == len(value):
            raise serializers.ValidationError("One or more groups not found.")
        return value

    def validate(self, attrs):
        if attrs["start_time"] >= attrs["end_time"]:
            raise serializers.ValidationError(
                "End time must be after start time."
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        group_ids = validated_data.pop("group_ids")
        virtual_class = VirtualClass.objects.create(**validated_data)
        virtual_class.groups.set(group_ids)
        return virtual_class

    @transaction.atomic
    def update(self, instance, validated_data):
        group_ids = validated_data.pop("group_ids", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if group_ids is not None:
            instance.groups.set(group_ids)

        return instance




class VirtualClassReadSerializer(serializers.ModelSerializer):

    groups = GroupNestedSerializer(many=True, read_only=True)

    class Meta:
        model = VirtualClass
        fields = [
            "id",
            "title",
            "url",
            "start_time",
            "end_time",
            "references",
            "notes",
            "groups",
            "created_at",
            "updated_at",
        ]