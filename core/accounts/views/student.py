from rest_framework import viewsets, mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from ..models import Student
from ..serializers import *
from ..filters import StudentFilter


class StudentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):

    queryset = Student.objects.select_related(
        "user", "parent"
    ).prefetch_related(
        "subjects_enrolled",
        "groups",
    ).all()

    serializer_class = StudentCreateSerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = StudentFilter

    search_fields = [
        "first_name",
        "last_name",
        "admission_number",
        "county",
    ]

    ordering_fields = [
        "first_name",
        "last_name",
        "created_at",
    ]

    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return StudentCreateSerializer
        return StudentReadSerializer