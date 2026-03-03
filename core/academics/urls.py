from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r"subjects", SubjectViewSet, basename="subject")
router.register(r"subject-tags", SubjectTagViewSet, basename="subject-tag")
router.register(r"teacher-subjects", TeacherSubjectViewSet, basename="teacher-subject")
router.register(r"student-subjects", StudentSubjectViewSet, basename="student-subject")
router.register(r"topics", TopicViewSet, basename="topic")
router.register(r"exercises", ExerciseViewSet, basename="exercise")
router.register(r"exercise-submissions", ExerciseSubmissionViewSet, basename="exercise-submissions")
router.register(r"exam-questions", ExamQuestionViewSet, basename="exam-questions")
router.register(r"exam-submissions", ExamSubmissionViewSet, basename="exam-submissions")
router.register(r"exam-results", ExamResultViewSet, basename="exam-results")

# urlpatterns = router.urls

urlpatterns = [
    path(
        "dashboard/teacher/stats/",
        TeacherDashboardStatsView.as_view(),
        name="teacher-dashboard-stats",
    ),
    path(
        "dashboard/student/<uuid:student_id>/stats/",
        StudentDashboardStatsView.as_view(),
        name="student-dashboard-stats",
    ),
    path(
        "dashboard/teacher/exercises/",
        TeacherExerciseDashboardView.as_view(),
        name="teacher-exercise-dashboard",
    ),
    path(
        "dashboard/student/<uuid:student_id>/exercises/",
        StudentExerciseDashboardView.as_view(),
        name="student-exercise-dashboard",
    ),
]+ router.urls