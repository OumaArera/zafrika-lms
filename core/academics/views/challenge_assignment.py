from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import ChallengeAssignment
from ..serializers import ChallengeAssignmentSerializer

class ChallengeAssignmentViewSet(viewsets.ModelViewSet):
    queryset = ChallengeAssignment.objects.select_related("day", "day__challenge")
    serializer_class = ChallengeAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()