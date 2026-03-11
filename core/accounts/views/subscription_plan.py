from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from ..models import SubscriptionPlan
from ..serializers import SubscriptionPlanSerializer


class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    """
    Subscription plans endpoint.

    - GET requests are public (AllowAny)
    - POST, PATCH, PUT, DELETE require authentication
    """

    serializer_class = SubscriptionPlanSerializer
    queryset = SubscriptionPlan.objects.all().order_by("price")

    def get_permissions(self):
        """
        Allow public read access but require authentication for writes.
        """
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return [AllowAny()]
        return [IsAuthenticated()]