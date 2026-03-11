from rest_framework import serializers
from ..models import SubscriptionPlan


class SubscriptionPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubscriptionPlan
        fields = [
            "id",
            "name",
            "tier",
            "duration",
            "price",
            "currency",
            "description",
            "notes_access",
            "exercises_access",
            "exams_access",
            "virtual_classes_access",
            "active",
        ]