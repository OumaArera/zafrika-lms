import django_filters
from ..models import Exercise


class ExerciseFilter(django_filters.FilterSet):

    topic = django_filters.UUIDFilter(field_name="topic__id")
    subject = django_filters.UUIDFilter(field_name="subject__id")
    level = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = Exercise
        fields = ["topic", "subject", "level"]