from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from ..models import TeacherSubject
from ..serializers.teacher_subject import TeacherSubjectSerializer



class TeacherSubjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing subjects assigned to teachers.
    Supports full CRUD.
    """
    queryset = TeacherSubject.objects.select_related("teacher", "subject").all()
    serializer_class = TeacherSubjectSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["teacher", "subject", "is_active"]