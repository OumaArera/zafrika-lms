from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import Subscription
from ..serializers import SubscriptionSerializer

class SubscriptionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.select_related("student").prefetch_related(
        "subjects", "topics", "virtual_classes"
    )

    def get_queryset(self):
        """
        Optionally filter subscriptions for a student and order by active first,
        then by end_date descending.
        """
        queryset = self.queryset
        student_id = self.request.query_params.get("student_id")

        if student_id:
            queryset = queryset.filter(student_id=student_id)

        # Active subscriptions first, then by end_date descending
        queryset = queryset.order_by("-active", "-end_date")
        return queryset

    def perform_create(self, serializer):
        # The teacher-admin creating the subscription
        serializer.save(student_id=self.request.data.get("student_id"))