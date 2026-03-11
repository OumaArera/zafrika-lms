from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import Subscription
from ..serializers import SubscriptionSerializer
from django_filters.rest_framework import DjangoFilterBackend


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

