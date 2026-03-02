from rest_framework import viewsets, mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from ..models import Teacher
from ..serializers import TeacherCreateSerializer, TeacherReadSerializer
from ..middleware import IsAdmin
from ..filters import TeacherFilter


class TeacherViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):

    queryset = Teacher.objects.select_related("user").all()

    permission_classes = [IsAdmin]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = TeacherFilter

    search_fields = [
        "first_name",
        "last_name",
        "tsc_number",
        "county",
    ]

    ordering_fields = [
        "created_at",
        "first_name",
        "last_name",
        "county",
    ]

    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return TeacherCreateSerializer
        return TeacherReadSerializer