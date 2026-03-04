
import django_filters
from ..models import Topic


class TopicFilter(django_filters.FilterSet):

    subject = django_filters.UUIDFilter(field_name="subject__id")
    author = django_filters.UUIDFilter(field_name="author__id")

    class Meta:
        model = Topic
        fields = ["subject", "author"]