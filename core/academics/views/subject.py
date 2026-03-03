from rest_framework import viewsets
from ..models import Subject, SubjectTag
from ..serializers import *
from ...accounts.middleware import *

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAdmin]


class SubjectTagViewSet(viewsets.ModelViewSet):
    queryset = SubjectTag.objects.select_related("subject").all()
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return SubjectTagWriteSerializer
        return SubjectTagReadSerializer