from rest_framework import viewsets, mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from ..models import Group
from ..serializers import GroupCreateUpdateSerializer


class GroupViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    queryset = Group.objects.prefetch_related(
        "students",
        "students__user",
    )

    serializer_class = GroupCreateUpdateSerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        "name",
        "students",
    ]

    search_fields = [
        "name",
        "students__first_name",
        "students__last_name",
        "students__admission_number",
    ]

    ordering_fields = [
        "name",
        "created_at",
    ]

    ordering = ["-created_at"]
