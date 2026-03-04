from rest_framework import viewsets, mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from ..models import ExamSubmission
from ..serializers.exam_submission import (
    ExamSubmissionCreateSerializer,
    ExamSubmissionReadSerializer,
)
from django.db.models import F, FloatField, ExpressionWrapper


class ExamSubmissionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    queryset = ExamSubmission.objects.select_related(
        "student",
        "exam",
        "supervisor",
        "result",
    ).prefetch_related(
        "images"
    ).annotate(
        percentage=ExpressionWrapper(
            (F("result__score") * 100.0) / F("result__out_of"),
            output_field=FloatField()
    )
)

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_fields = [
        "student",
        "exam",
        "supervisor",
        "is_marked",
    ]

    ordering_fields = [
        "created_at",
        "is_marked",
    ]

    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ExamSubmissionCreateSerializer
        return ExamSubmissionReadSerializer