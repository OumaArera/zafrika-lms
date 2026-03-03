from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from ..models import StudentSubject
from ..serializers import StudentSubjectSerializer

class StudentSubjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing subjects assigned to students.
    Supports full CRUD.
    """
    queryset = StudentSubject.objects.select_related("student", "subject").all()
    serializer_class = StudentSubjectSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student", "subject", "is_active"]