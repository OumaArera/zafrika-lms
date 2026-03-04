from rest_framework import viewsets, mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from ..models import Parent
from ..serializers import ParentSerializer
from ..filters import ParentFilter


class ParentViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):

    queryset = Parent.objects.all()

    serializer_class = ParentSerializer


    # Filtering
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = ParentFilter

    # Optional search
    search_fields = [
        "first_name",
        "last_name",
        "id_number",
        "phone_number",
        "email",
    ]

    # Optional ordering
    ordering_fields = [
        "first_name",
        "last_name",
        "created_at",
    ]

    ordering = ["-created_at"]