"""
Exercise Dashboard analytics — Teacher & Student dashboards.

Key differences from Exam analytics
-------------------------------------
- Exercise has NO score/result — all metrics are count-based only.
- Exercise.level  : beginner | intermediate | expert  (not scout/explorer/legend)
- Exercise.subject: direct FK to Subject (no SubjectTag intermediary)
- Exercise.topic  : direct FK to Topic
- No grade field on Exercise — breakdowns are by subject + topic instead.
- is_marked + supervisor_comment are the only quality signals available.

ORM rules (same as exam analytics — repeated here for clarity)
--------------------------------------------------------------
1. Never use keyword aliases in .values() that shadow a real model FK column.
   Use positional string paths ("student__id") and remap in Python.
2. One .values().annotate() per queryset — never chain a second .values()
   with re-declared expressions.

Query budget
------------
Teacher exercise dashboard : 4 queries
Student exercise dashboard : 3 queries
"""

# ============================================================
# exercise_analytics/queries.py
# ============================================================

from django.db.models import Count, F, Q
from django.db.models.functions import Round

from ..models import Exercise, ExerciseSubmission
from ...accounts.models import Student


# ------------------------------------------------------------------
# Reusable annotation blocks
# No averages — exercises are unscored. Metrics are submission counts only.
# ------------------------------------------------------------------

EXERCISE_LEVEL_COUNT_ANNOTATIONS = dict(
    beginner_count=Count(
        "id", filter=Q(exercise__level=Exercise.Levels.BEGINNER)
    ),
    intermediate_count=Count(
        "id", filter=Q(exercise__level=Exercise.Levels.INTERMEDIATE)
    ),
    expert_count=Count(
        "id", filter=Q(exercise__level=Exercise.Levels.EXPERT)
    ),
)

MARKED_ANNOTATION = dict(
    marked_count=Count("id", filter=Q(is_marked=True)),
    unmarked_count=Count("id", filter=Q(is_marked=False)),
)

COMMENTED_ANNOTATION = dict(
    commented_count=Count(
        "id", filter=Q(supervisor_comment__isnull=False) & ~Q(supervisor_comment="")
    ),
)


# ------------------------------------------------------------------
# 1. Teacher Exercise Dashboard — system-wide stats
# ------------------------------------------------------------------

def get_teacher_exercise_stats() -> dict:
    """
    System-wide exercise submission analytics for teachers.

    DB queries: 4
      Q1 — overall level distribution
      Q2 — per-subject breakdown with level counts + marked/commented rates
      Q3 — per-topic breakdown with level counts + marked/commented rates
      Q4 — most active students (top 20 by submission count)

    Returns: {
        "overall": {
            "total_submissions": int,
            "marked_count": int,
            "unmarked_count": int,
            "commented_count": int,
            "unique_students": int,
            "unique_exercises": int,
        },
        "level_distribution": {
            "beginner":     {"total_submissions": int, "unique_students": int},
            "intermediate": { ... },
            "expert":       { ... },
        },
        "per_subject": [
            {
                "subject_name": str,
                "total_submissions": int,
                "unique_students": int,
                "marked_count": int,
                "unmarked_count": int,
                "commented_count": int,
                "beginner_count": int,
                "intermediate_count": int,
                "expert_count": int,
            },
            ...  ordered by subject_name asc
        ],
        "per_topic": [
            {
                "subject_name": str,
                "topic_name": str,
                "total_submissions": int,
                "unique_students": int,
                "marked_count": int,
                "commented_count": int,
                "beginner_count": int,
                "intermediate_count": int,
                "expert_count": int,
            },
            ...  ordered by subject_name, topic_name asc
        ],
        "most_active_students": [
            {
                "student_id": UUID,
                "first_name": str,
                "last_name": str,
                "total_submissions": int,
                "marked_count": int,
                "commented_count": int,
            },
            ...  (max 20, descending total_submissions)
        ],
    }
    """
    base_qs = ExerciseSubmission.objects.select_related(
        "exercise__subject",
        "exercise__topic",
        "student",
    )

    # Q1 — Overall summary + level distribution (2 aggregations, 2 queries)
    overall_raw = base_qs.aggregate(
        total_submissions=Count("id"),
        unique_students=Count("student", distinct=True),
        unique_exercises=Count("exercise", distinct=True),
        **MARKED_ANNOTATION,
        **COMMENTED_ANNOTATION,
    )

    overall = {
        "total_submissions": overall_raw["total_submissions"],
        "marked_count": overall_raw["marked_count"],
        "unmarked_count": overall_raw["unmarked_count"],
        "commented_count": overall_raw["commented_count"],
        "unique_students": overall_raw["unique_students"],
        "unique_exercises": overall_raw["unique_exercises"],
    }

    level_rows = (
        base_qs
        .values("exercise__level")
        .annotate(
            total_submissions=Count("id"),
            unique_students=Count("student", distinct=True),
        )
        .order_by("exercise__level")
    )

    level_distribution: dict = {
        row["exercise__level"]: {
            "total_submissions": row["total_submissions"],
            "unique_students": row["unique_students"],
        }
        for row in level_rows
    }

    # Q2 — Per-subject breakdown
    per_subject_qs = (
        base_qs
        .values(subject_name=F("exercise__subject__name"))
        .annotate(
            total_submissions=Count("id"),
            unique_students=Count("student", distinct=True),
            **EXERCISE_LEVEL_COUNT_ANNOTATIONS,
            **MARKED_ANNOTATION,
            **COMMENTED_ANNOTATION,
        )
        .order_by("subject_name")
    )

    per_subject = [
        {
            "subject_name": row["subject_name"],
            "total_submissions": row["total_submissions"],
            "unique_students": row["unique_students"],
            "marked_count": row["marked_count"],
            "unmarked_count": row["unmarked_count"],
            "commented_count": row["commented_count"],
            "beginner_count": row["beginner_count"],
            "intermediate_count": row["intermediate_count"],
            "expert_count": row["expert_count"],
        }
        for row in per_subject_qs
    ]

    # Q3 — Per-topic breakdown (includes parent subject for context)
    per_topic_qs = (
        base_qs
        .values(
            subject_name=F("exercise__subject__name"),
            topic_name=F("exercise__topic__title"),
        )
        .annotate(
            total_submissions=Count("id"),
            unique_students=Count("student", distinct=True),
            **EXERCISE_LEVEL_COUNT_ANNOTATIONS,
            **MARKED_ANNOTATION,
            **COMMENTED_ANNOTATION,
        )
        .order_by("subject_name", "topic_name")
    )

    per_topic = [
        {
            "subject_name": row["subject_name"],
            "topic_name": row["topic_name"],
            "total_submissions": row["total_submissions"],
            "unique_students": row["unique_students"],
            "marked_count": row["marked_count"],
            "commented_count": row["commented_count"],
            "beginner_count": row["beginner_count"],
            "intermediate_count": row["intermediate_count"],
            "expert_count": row["expert_count"],
        }
        for row in per_topic_qs
    ]

    # Q4 — Top 20 most active students by total submissions
    # Use positional string paths — keyword alias `student_id` would conflict
    # with the FK column on ExerciseSubmission.
    most_active_qs = (
        base_qs
        .values(
            "student__id",
            "student__first_name",
            "student__last_name",
        )
        .annotate(
            total_submissions=Count("id"),
            **MARKED_ANNOTATION,
            **COMMENTED_ANNOTATION,
        )
        .order_by(F("total_submissions").desc())[:20]
    )

    most_active_students = [
        {
            "student_id": row["student__id"],
            "first_name": row["student__first_name"],
            "last_name": row["student__last_name"],
            "total_submissions": row["total_submissions"],
            "marked_count": row["marked_count"],
            "commented_count": row["commented_count"],
        }
        for row in most_active_qs
    ]

    return {
        "overall": overall,
        "level_distribution": level_distribution,
        "per_subject": per_subject,
        "per_topic": per_topic,
        "most_active_students": most_active_students,
    }


# ------------------------------------------------------------------
# 2. Student Exercise Dashboard — single student stats
# ------------------------------------------------------------------

def get_student_exercise_stats(student_id) -> dict:
    """
    Personal exercise analytics for one student.

    DB queries: 3
      Q1 — overall aggregate (.aggregate → no GROUP BY, single round-trip)
      Q2 — per-subject breakdown
      Q3 — per-topic breakdown

    Returns: {
        "overall": {
            "total_submissions": int,
            "marked_count": int,
            "unmarked_count": int,
            "commented_count": int,
            "beginner_count": int,
            "intermediate_count": int,
            "expert_count": int,
        },
        "per_subject": [
            {
                "subject_name": str,
                "total_submissions": int,
                "marked_count": int,
                "commented_count": int,
                "beginner_count": int,
                "intermediate_count": int,
                "expert_count": int,
            },
            ...  ordered by subject_name asc
        ],
        "per_topic": [
            {
                "subject_name": str,
                "topic_name": str,
                "total_submissions": int,
                "marked_count": int,
                "commented_count": int,
                "beginner_count": int,
                "intermediate_count": int,
                "expert_count": int,
            },
            ...  ordered by subject_name, topic_name asc
        ],
    }
    """
    # Single base queryset — student filter applied once, reused across all queries
    base_qs = ExerciseSubmission.objects.filter(student_id=student_id).select_related(
        "exercise__subject",
        "exercise__topic",
    )

    # Q1 — Overall summary (.aggregate → single DB round-trip, no GROUP BY)
    overall_raw = base_qs.aggregate(
        total_submissions=Count("id"),
        **EXERCISE_LEVEL_COUNT_ANNOTATIONS,
        **MARKED_ANNOTATION,
        **COMMENTED_ANNOTATION,
    )

    overall = {
        "total_submissions": overall_raw["total_submissions"],
        "marked_count": overall_raw["marked_count"],
        "unmarked_count": overall_raw["unmarked_count"],
        "commented_count": overall_raw["commented_count"],
        "beginner_count": overall_raw["beginner_count"],
        "intermediate_count": overall_raw["intermediate_count"],
        "expert_count": overall_raw["expert_count"],
    }

    # Q2 — Per-subject breakdown
    per_subject_qs = (
        base_qs
        .values(subject_name=F("exercise__subject__name"))
        .annotate(
            total_submissions=Count("id"),
            **EXERCISE_LEVEL_COUNT_ANNOTATIONS,
            **MARKED_ANNOTATION,
            **COMMENTED_ANNOTATION,
        )
        .order_by("subject_name")
    )

    per_subject = [
        {
            "subject_name": row["subject_name"],
            "total_submissions": row["total_submissions"],
            "marked_count": row["marked_count"],
            "commented_count": row["commented_count"],
            "beginner_count": row["beginner_count"],
            "intermediate_count": row["intermediate_count"],
            "expert_count": row["expert_count"],
        }
        for row in per_subject_qs
    ]

    # Q3 — Per-topic breakdown
    per_topic_qs = (
        base_qs
        .values(
            subject_name=F("exercise__subject__name"),
            topic_name=F("exercise__topic__title"),
        )
        .annotate(
            total_submissions=Count("id"),
            **EXERCISE_LEVEL_COUNT_ANNOTATIONS,
            **MARKED_ANNOTATION,
            **COMMENTED_ANNOTATION,
        )
        .order_by("subject_name", "topic_name")
    )

    per_topic = [
        {
            "subject_name": row["subject_name"],
            "topic_name": row["topic_name"],
            "total_submissions": row["total_submissions"],
            "marked_count": row["marked_count"],
            "commented_count": row["commented_count"],
            "beginner_count": row["beginner_count"],
            "intermediate_count": row["intermediate_count"],
            "expert_count": row["expert_count"],
        }
        for row in per_topic_qs
    ]

    return {
        "overall": overall,
        "per_subject": per_subject,
        "per_topic": per_topic,
    }


# ============================================================
# exercise_analytics/serializers.py
# ============================================================

from rest_framework import serializers


# ---- Shared ----

class ExerciseLevelMixin(serializers.Serializer):
    """Level count fields shared across multiple serializers."""
    beginner_count = serializers.IntegerField()
    intermediate_count = serializers.IntegerField()
    expert_count = serializers.IntegerField()


class MarkedMixin(serializers.Serializer):
    """Marked/commented count fields shared across multiple serializers."""
    marked_count = serializers.IntegerField()
    commented_count = serializers.IntegerField()


# ---- Teacher serializers ----

class ExerciseOverallTeacherSerializer(serializers.Serializer):
    total_submissions = serializers.IntegerField()
    marked_count = serializers.IntegerField()
    unmarked_count = serializers.IntegerField()
    commented_count = serializers.IntegerField()
    unique_students = serializers.IntegerField()
    unique_exercises = serializers.IntegerField()


class ExerciseLevelDistributionSerializer(serializers.Serializer):
    total_submissions = serializers.IntegerField()
    unique_students = serializers.IntegerField()


class ExercisePerSubjectTeacherSerializer(ExerciseLevelMixin, MarkedMixin):
    subject_name = serializers.CharField()
    total_submissions = serializers.IntegerField()
    unique_students = serializers.IntegerField()
    unmarked_count = serializers.IntegerField()


class ExercisePerTopicTeacherSerializer(ExerciseLevelMixin, MarkedMixin):
    subject_name = serializers.CharField()
    topic_name = serializers.CharField()
    total_submissions = serializers.IntegerField()
    unique_students = serializers.IntegerField()


class MostActiveStudentSerializer(MarkedMixin):
    student_id = serializers.UUIDField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    total_submissions = serializers.IntegerField()


class TeacherExerciseDashboardSerializer(serializers.Serializer):
    overall = ExerciseOverallTeacherSerializer()
    level_distribution = serializers.DictField(
        child=ExerciseLevelDistributionSerializer()
    )
    per_subject = ExercisePerSubjectTeacherSerializer(many=True)
    per_topic = ExercisePerTopicTeacherSerializer(many=True)
    most_active_students = MostActiveStudentSerializer(many=True)


# ---- Student serializers ----

class ExerciseOverallStudentSerializer(ExerciseLevelMixin, MarkedMixin):
    total_submissions = serializers.IntegerField()
    unmarked_count = serializers.IntegerField()


class ExercisePerSubjectStudentSerializer(ExerciseLevelMixin, MarkedMixin):
    subject_name = serializers.CharField()
    total_submissions = serializers.IntegerField()


class ExercisePerTopicStudentSerializer(ExerciseLevelMixin, MarkedMixin):
    subject_name = serializers.CharField()
    topic_name = serializers.CharField()
    total_submissions = serializers.IntegerField()


class StudentExerciseDashboardSerializer(serializers.Serializer):
    overall = ExerciseOverallStudentSerializer()
    per_subject = ExercisePerSubjectStudentSerializer(many=True)
    per_topic = ExercisePerTopicStudentSerializer(many=True)


# ============================================================
# exercise_analytics/views.py
# ============================================================

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response


class TeacherExerciseDashboardView(GenericAPIView):
    """
    GET /api/v1/dashboard/teacher/exercises/

    System-wide exercise submission analytics:
    - Overall totals (submissions, marked, commented, unique students/exercises)
    - Level distribution (beginner / intermediate / expert)
    - Per-subject breakdown with level counts and marked/commented rates
    - Per-topic breakdown with level counts and marked/commented rates
    - Top 20 most active students
    """

    serializer_class = TeacherExerciseDashboardSerializer

    def get(self, request: Request) -> Response:
        data = get_teacher_exercise_stats()
        serializer = self.get_serializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentExerciseDashboardView(GenericAPIView):
    """
    GET /api/v1/dashboard/student/<student_id>/exercises/

    Personal exercise analytics for a single student:
    - Overall level counts and marked/commented rates
    - Per-subject breakdown
    - Per-topic breakdown

    URL kwargs:
        student_id — UUID primary key of the Student record.
    """

    serializer_class = StudentExerciseDashboardSerializer

    def _get_student(self, student_id) -> tuple:
        """Return (student, None) or (None, 404 Response)."""
        try:
            return Student.objects.only("id").get(id=student_id), None
        except Student.DoesNotExist:
            return None, Response(
                {"error": "Student not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def get(self, request: Request, student_id) -> Response:
        student, error = self._get_student(student_id)
        if error:
            return error

        data = get_student_exercise_stats(student_id=student.id)
        serializer = self.get_serializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================================
# exercise_analytics/urls.py
# ============================================================
#
# from django.urls import path
# from .views import TeacherExerciseDashboardView, StudentExerciseDashboardView
#
# urlpatterns = [
#     path(
#         "dashboard/teacher/exercises/",
#         TeacherExerciseDashboardView.as_view(),
#         name="teacher-exercise-dashboard",
#     ),
#     path(
#         "dashboard/student/<uuid:student_id>/exercises/",
#         StudentExerciseDashboardView.as_view(),
#         name="student-exercise-dashboard",
#     ),
# ]