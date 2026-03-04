from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from ..filters.virtual_class import VirtualClassFilter
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import VirtualClass
from ..serializers.virtual_class import (
    VirtualClassCreateUpdateSerializer,
    VirtualClassReadSerializer
)


class VirtualClassViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = VirtualClassFilter
    ordering_fields = ['start_time', 'end_time', 'title']
    ordering = ['-start_time']

    def get_queryset(self):
        queryset = VirtualClass.objects.prefetch_related(
            "groups",
            "groups__students"
        )
        user = self.request.user

        if user.role in ["teacher", "admin", "teacher-admin"]:
            return queryset

        if user.role == "student":
            try:
                student = user.student_profile
            except AttributeError:
                return VirtualClass.objects.none()

            return queryset.filter(groups__students=student).distinct()

        return VirtualClass.objects.none()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return VirtualClassCreateUpdateSerializer
        return VirtualClassReadSerializer