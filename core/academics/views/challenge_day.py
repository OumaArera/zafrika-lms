from rest_framework import viewsets
from ..models import ChallengeDay
from ..serializers import ChallengeDayCreateSerializer

class ChallengeDayViewSet(viewsets.ModelViewSet):
    queryset = ChallengeDay.objects.select_related("challenge")
    serializer_class = ChallengeDayCreateSerializer

    def perform_create(self, serializer):
        serializer.save()

  

