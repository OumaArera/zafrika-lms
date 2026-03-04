import django_filters
from ..models import Parent


class ParentFilter(django_filters.FilterSet):

    first_name = django_filters.CharFilter(lookup_expr="icontains")
    last_name = django_filters.CharFilter(lookup_expr="icontains")
    id_number = django_filters.CharFilter(lookup_expr="exact")
    phone_number = django_filters.CharFilter(lookup_expr="icontains")
    email = django_filters.CharFilter(lookup_expr="icontains")
    date_of_birth = django_filters.DateFilter()

    class Meta:
        model = Parent
        fields = [
            "id_number",
            "date_of_birth",
        ]