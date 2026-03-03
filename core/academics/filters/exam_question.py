import django_filters
from ..models import ExamQuestion


class ExamQuestionFilter(django_filters.FilterSet):

    subject_tag = django_filters.UUIDFilter(field_name="subject_tag__id")
    grade = django_filters.CharFilter(field_name="grade")
    level = django_filters.CharFilter(field_name="level")

    class Meta:
        model = ExamQuestion
        fields = [
            "subject_tag",
            "grade",
            "level",
        ]