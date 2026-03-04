import django_filters
from django.utils import timezone
from ..models import VirtualClass
from datetime import timedelta, datetime, date

class VirtualClassFilter(django_filters.FilterSet):
    date_range = django_filters.CharFilter(method='filter_by_date_range')

    class Meta:
        model = VirtualClass
        fields = []

    def filter_by_date_range(self, queryset, name, value):
        today = timezone.localdate()
        print(f"Today: {today}")
        if value == "today":
            return queryset.filter(start_time__date=today)
        elif value == "tomorrow":
            return queryset.filter(start_time__date=today + timedelta(days=1))
        elif value == "this_week":
            start_of_week = today - timedelta(days=today.weekday())  # Monday
            end_of_week = start_of_week + timedelta(days=6)
            return queryset.filter(start_time__date__range=[start_of_week, end_of_week])
        elif value == "next_week":
            start_of_next_week = today - timedelta(days=today.weekday()) + timedelta(days=7)
            end_of_next_week = start_of_next_week + timedelta(days=6)
            return queryset.filter(start_time__date__range=[start_of_next_week, end_of_next_week])
        elif value == "last_week":
            start_of_last_week = today - timedelta(days=today.weekday() + 7)
            end_of_last_week = start_of_last_week + timedelta(days=6)
            return queryset.filter(start_time__date__range=[start_of_last_week, end_of_last_week])
        elif value == "this_month":
            first_day = today.replace(day=1)
            if today.month == 12:
                last_day = first_day.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                last_day = first_day.replace(month=today.month + 1, day=1) - timedelta(days=1)
            return queryset.filter(start_time__date__range=[first_day, last_day])
        return queryset