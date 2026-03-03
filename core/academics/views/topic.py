from rest_framework import viewsets, mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from ..models import Topic
from ..serializers import (
    TopicCreateUpdateSerializer,
    TopicReadSerializer,
)
from ..filters.topic import TopicFilter


class TopicViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    queryset = Topic.objects.select_related(
        "subject",
        "author",
        "author__user",
    ).prefetch_related(
        "exercises"
    )

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = TopicFilter

    # Case-insensitive search
    search_fields = [
        "title",
        "description",
    ]

    ordering_fields = [
        "created_at",
        "title",
    ]

    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return TopicCreateUpdateSerializer
        return TopicReadSerializer