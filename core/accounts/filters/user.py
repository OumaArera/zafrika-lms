import django_filters
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFilter(django_filters.FilterSet):

    role = django_filters.CharFilter(lookup_expr="iexact")
    status = django_filters.CharFilter(lookup_expr="iexact")
    is_verified = django_filters.BooleanFilter()

    class Meta:
        model = User
        fields = ["role", "status", "is_verified"]