from rest_framework import serializers
from ..models import Subscription
from ..serializers import StudentNestedSerializer
from .subscription_plan import SubscriptionPlanSerializer


class SubscriptionSerializer(serializers.ModelSerializer):

    student = StudentNestedSerializer(read_only=True)

    plan = SubscriptionPlanSerializer(read_only=True)

    student_id = serializers.UUIDField(write_only=True)

    plan_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Subscription
        fields = [
            "id",
            "student",
            "plan",
            "student_id",
            "plan_id",
            "start_date",
            "end_date",
            "active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "start_date",
            "end_date",
            "created_at",
            "updated_at",
        ]