from rest_framework import viewsets, mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from ..models import ExerciseSubmission
from ..serializers.exercise_submission import (
    ExerciseSubmissionCreateSerializer,
    ExerciseSubmissionReadSerializer,
)


class ExerciseSubmissionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    queryset = ExerciseSubmission.objects.select_related(
        "student",
        "exercise",
        "supervisor",
    ).prefetch_related(
        "images"
    )

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_fields = [
        "student",
        "exercise",
        "supervisor",
    ]

    ordering_fields = [
        "created_at",
    ]

    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ExerciseSubmissionCreateSerializer
        return ExerciseSubmissionReadSerializer