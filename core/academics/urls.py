from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r"subjects", SubjectViewSet, basename="subject")
router.register(r"subject-tags", SubjectTagViewSet, basename="subject-tag")
router.register(r"teacher-subjects", TeacherSubjectViewSet, basename="teacher-subject")
router.register(r"student-subjects", StudentSubjectViewSet, basename="student-subject")
router.register(r"topics", TopicViewSet, basename="topic")
router.register(r"exercises", ExerciseViewSet, basename="exercise")

urlpatterns = router.urls