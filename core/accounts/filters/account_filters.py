import django_filters
from ..models import  Student, Teacher



class StudentFilter(django_filters.FilterSet):
    admission_number = django_filters.CharFilter()
    county = django_filters.CharFilter(lookup_expr="icontains")
    current_school_level = django_filters.CharFilter()

    class Meta:
        model = Student
        fields = ["county", "current_school_level"]


class TeacherFilter(django_filters.FilterSet):
    county = django_filters.CharFilter(lookup_expr="icontains")
    tsc_number = django_filters.CharFilter()

    class Meta:
        model = Teacher
        fields = ["county"]