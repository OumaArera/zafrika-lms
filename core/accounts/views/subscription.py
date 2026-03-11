from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta

from ..models import Subscription, SubscriptionPlan
from ..serializers import SubscriptionSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer

    queryset = Subscription.objects.select_related("student", "plan")

    filter_backends = [DjangoFilterBackend]

    filterset_fields = ["student", "plan", "active"]

    def perform_create(self, serializer):
        serializer.save(
            student_id=self.request.data.get("student_id"),
            plan_id=self.request.data.get("plan_id")
        )


class PlanStatsView(APIView):
    """
    Provides analytics for subscription plans.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):

        now = timezone.now()
        twelve_months_ago = now - timedelta(days=365)

        # Total available plans
        total_plans = SubscriptionPlan.objects.count()

        # Total subscriptions
        total_subscriptions = Subscription.objects.count()

        # Active subscriptions
        active_subscriptions = Subscription.objects.filter(active=True).count()

        # Total revenue (sum of plan prices for subscriptions)
        total_revenue = Subscription.objects.select_related("plan").aggregate(
            revenue=Sum("plan__price")
        )["revenue"] or 0

        # Revenue distribution for the last 12 months
        monthly_revenue = (
            Subscription.objects.filter(created_at__gte=twelve_months_ago)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(
                revenue=Sum("plan__price"),
                subscriptions=Count("id")
            )
            .order_by("month")
        )

        # Plan popularity (how many subscriptions per plan)
        plan_distribution = (
            Subscription.objects.values("plan__name")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        data = {
            "total_plans": total_plans,
            "total_subscriptions": total_subscriptions,
            "active_subscriptions": active_subscriptions,
            "total_revenue": total_revenue,
            "monthly_revenue_last_12_months": list(monthly_revenue),
            "plan_distribution": list(plan_distribution),
        }

        return Response(data)
