from rest_framework import viewsets, mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth import get_user_model
from ..serializers import UserReadSerializer
from ..filters import UserFilter
from ..middleware import IsAdmin


User = get_user_model()


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):

    queryset = User.objects.all().only(
        "id",
        "username",
        "phone_number",
        "email",
        "role",
        "status",
        "is_verified",
        "must_change_password",
        "created_at",
    )

    serializer_class = UserReadSerializer

    permission_classes = [IsAdmin]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = UserFilter

    search_fields = [
        "username",
        "phone_number",
        "email",
    ]

    ordering_fields = [
        "created_at",
        "username",
        "role",
    ]

    ordering = ["-created_at"]