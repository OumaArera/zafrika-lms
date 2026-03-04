from rest_framework import viewsets, mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from ..models import Exercise
from ..serializers import (
    ExerciseCreateUpdateSerializer,
    ExerciseReadSerializer,
)
from ..filters import ExerciseFilter


class ExerciseViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    queryset = Exercise.objects.select_related(
        "topic",
        "subject",
        "topic__subject",
        "topic__author",
    ).all()

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = ExerciseFilter

    # Case-insensitive search
    search_fields = [
        "title",
    ]

    ordering_fields = [
        "created_at",
        "title",
    ]

    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ExerciseCreateUpdateSerializer
        return ExerciseReadSerializer