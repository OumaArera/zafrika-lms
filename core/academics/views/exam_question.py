from rest_framework import viewsets, mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from ..models import ExamQuestion
from ..serializers.exam_question import (
    ExamQuestionCreateUpdateSerializer,
    ExamQuestionReadSerializer,
)
from ..filters.exam_question import ExamQuestionFilter


class ExamQuestionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    queryset = ExamQuestion.objects.select_related(
        "subject_tag",
        "subject_tag__subject",
    )

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = ExamQuestionFilter

    # Strong case-insensitive search
    search_fields = [
        "title",
        "instructions",
        "content",
    ]

    ordering_fields = [
        "created_at",
        "grade",
        "level",
        "title",
    ]

    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ExamQuestionCreateUpdateSerializer
        return ExamQuestionReadSerializer