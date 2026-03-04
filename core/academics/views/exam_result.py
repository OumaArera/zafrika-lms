from rest_framework import viewsets, mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from ..models import ExamResult
from ..serializers.exam_result import ExamResultSerializer


class ExamResultViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    queryset = ExamResult.objects.select_related(
        "exam_submission",
        "exam_submission__student",
        "exam_submission__exam",
    )

    serializer_class = ExamResultSerializer

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_fields = [
        "exam_submission",
        "exam_submission__student",
        "exam_submission__exam",
    ]

    ordering_fields = ["score", "created_at"]
    ordering = ["-created_at"]