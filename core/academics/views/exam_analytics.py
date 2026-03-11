"""
Dashboard analytics — Teacher & Student dashboards.

Key ORM rules applied to avoid runtime errors
----------------------------------------------
1. Never use keyword aliases in .values() that shadow a real model field name.
   e.g.  student_id=F("student__id")  conflicts with the physical FK column
   `student_id` on ExamSubmission → Django raises:
       ValueError: The annotation 'student_id' conflicts with a field on the model.
   Fix: pass the field path as a positional string ("student__id") and remap
   the double-underscore key to a clean name in a Python list comprehension.

2. Never chain .values().annotate().values() with re-declared Count/Avg
   expressions. The second .values() re-enters the annotation pipeline and
   can silently duplicate or conflict with already-computed names.
   Fix: one .values().annotate() per queryset, then remap in Python.

3. Averages use raw AVG(result__score). Submissions without a linked
   ExamResult are excluded via filter=Q(result__isnull=False) so they
   don't pollute counts or produce division errors.

Query budget
------------
Teacher dashboard : 4 queries (level dist | per-grade | subject-tag | top-20)
Student dashboard : 3 queries (overall aggregate | per-grade | per-subject×grade)
"""

# ============================================================
# analytics/queries.py
# ============================================================


from django.db.models import Avg, Count, ExpressionWrapper, F, FloatField, Q
from django.db.models.functions import Round
from ..models import ExamQuestion, ExamSubmission
from ...accounts.models import Student


# ------------------------------------------------------------------
# Reusable annotation blocks
# ------------------------------------------------------------------

LEVEL_COUNT_ANNOTATIONS = dict(
    scout_count=Count(
        "id", filter=Q(exam__level=ExamQuestion.LevelChoices.SCOUT)
    ),
    explorer_count=Count(
        "id", filter=Q(exam__level=ExamQuestion.LevelChoices.EXPLORER)
    ),
    legend_count=Count(
        "id", filter=Q(exam__level=ExamQuestion.LevelChoices.LEGEND)
    ),
)



def _pct_avg_expr(extra_filter: Q = Q()) -> Round:
    """
    AVG((score / out_of) * 100) — percentage-normalised average.
    Submissions without a linked ExamResult are excluded via result__isnull=False.
    Submissions where out_of is 0 are also excluded to avoid division by zero.
    """
    safe_filter = extra_filter & Q(result__isnull=False) & Q(result__out_of__gt=0)
    return Round(
        Avg(
            ExpressionWrapper(
                F("result__score") / F("result__out_of") * 100,
                output_field=FloatField(),
            ),
            filter=safe_filter,
        ),
        2,
    )


def _pct_avg_for_level(level: str) -> Round:
    """Percentage-normalised AVG scoped to one exam level."""
    return _pct_avg_expr(extra_filter=Q(exam__level=level))


# Replace the old LEVEL_AVG_ANNOTATIONS and OVERALL_AVG_ANNOTATION dicts:

LEVEL_AVG_ANNOTATIONS = dict(
    scout_avg_score=_pct_avg_for_level(ExamQuestion.LevelChoices.SCOUT),
    explorer_avg_score=_pct_avg_for_level(ExamQuestion.LevelChoices.EXPLORER),
    legend_avg_score=_pct_avg_for_level(ExamQuestion.LevelChoices.LEGEND),
)

OVERALL_AVG_ANNOTATION = dict(
    overall_avg_score=_pct_avg_expr(),
)

# ------------------------------------------------------------------
# 1. Teacher Dashboard — system-wide stats
# ------------------------------------------------------------------

def get_teacher_dashboard_stats(grade: str | None = None) -> dict:
    """
    System-wide exam submission analytics, optionally scoped to one grade.

    DB queries: 4

    Args:
        grade: Optional ExamQuestion.GradeChoices value.

    Returns: {
        "level_distribution": {
            "scout":    {"total_submissions": int, "unique_students": int},
            "explorer": { ... },
            "legend":   { ... },
        },
        "per_grade": [
            {
                "grade": str,
                "total_submissions": int,
                "unique_students": int,
                "scout_count": int,
                "explorer_count": int,
                "legend_count": int,
            },
            ...
        ],
        "subject_distribution": [
            {
                "subject_name": str,
                "subject_tag_name": str,
                "total_submissions": int,
                "scout_count": int,
                "explorer_count": int,
                "legend_count": int,
                "overall_avg_score": Decimal | None,
            },
            ...
        ],
        "top_students": [
            {
                "student_id": UUID,
                "first_name": str,
                "last_name": str,
                "total_submissions": int,
                "marked_submissions": int,
                "overall_avg_score": Decimal | None,
            },
            ...  (max 20, descending avg score)
        ],
    }
    """
    base_qs = ExamSubmission.objects.select_related(
        "exam__subject_tag__subject",
        "student",
        "result",
    )

    if grade:
        base_qs = base_qs.filter(exam__grade=grade)

    # Q1 — Overall level distribution
    level_rows = (
        base_qs
        .values("exam__level")
        .annotate(
            total_submissions=Count("id"),
            unique_students=Count("student", distinct=True),
        )
        .order_by("exam__level")
    )

    level_distribution: dict = {
        row["exam__level"]: {
            "total_submissions": row["total_submissions"],
            "unique_students": row["unique_students"],
        }
        for row in level_rows
    }

    # Q2 — Per-grade × level breakdown
    per_grade_qs = (
        base_qs
        .values("exam__grade")
        .annotate(
            total_submissions=Count("id"),
            unique_students=Count("student", distinct=True),
            **LEVEL_COUNT_ANNOTATIONS,
        )
        .order_by("exam__grade")
    )

    per_grade = [
        {
            "grade": row["exam__grade"],
            "total_submissions": row["total_submissions"],
            "unique_students": row["unique_students"],
            "scout_count": row["scout_count"],
            "explorer_count": row["explorer_count"],
            "legend_count": row["legend_count"],
        }
        for row in per_grade_qs
    ]

    # Q3 — Subject-tag distribution with level counts + overall avg raw score
    subject_qs = (
        base_qs
        .values(
            subject_name=F("exam__subject_tag__subject__name"),
            subject_tag_name=F("exam__subject_tag__name"),
        )
        .annotate(
            total_submissions=Count("id"),
            **LEVEL_COUNT_ANNOTATIONS,
            **OVERALL_AVG_ANNOTATION,
        )
        .order_by("subject_name", "subject_tag_name")
    )

    subject_distribution = [
        {
            "subject_name": row["subject_name"],
            "subject_tag_name": row["subject_tag_name"],
            "total_submissions": row["total_submissions"],
            "scout_count": row["scout_count"],
            "explorer_count": row["explorer_count"],
            "legend_count": row["legend_count"],
            "overall_avg_score": row["overall_avg_score"],
        }
        for row in subject_qs
    ]

    # Q4 — Top 20 students by avg raw score
    # Use positional string paths ("student__id") NOT keyword aliases
    # (student_id=F("student__id")) — the latter conflicts with the real FK
    # column `student_id` on ExamSubmission and raises ValueError at runtime.
    # Q4 — Top 20 students by avg percentage score
    top_students_qs = (
        base_qs
        .values(
            "student__id",
            "student__first_name",
            "student__last_name",
        )
        .annotate(
            total_submissions=Count("id"),
            marked_submissions=Count("id", filter=Q(is_marked=True)),
            overall_avg_score=Round(
                Avg(
                    ExpressionWrapper(
                        F("result__score") / F("result__out_of") * 100,
                        output_field=FloatField(),
                    ),
                    filter=Q(result__isnull=False, result__out_of__gt=0),
                ),
                2,
            ),
        )
        .order_by(F("overall_avg_score").desc(nulls_last=True))[:20]
    )

    top_students = [
        {
            "student_id": row["student__id"],
            "first_name": row["student__first_name"],
            "last_name": row["student__last_name"],
            "total_submissions": row["total_submissions"],
            "marked_submissions": row["marked_submissions"],
            "overall_avg_score": row["overall_avg_score"],
        }
        for row in top_students_qs
    ]

    return {
        "level_distribution": level_distribution,
        "per_grade": per_grade,
        "subject_distribution": subject_distribution,
        "top_students": top_students,
    }


# ------------------------------------------------------------------
# 2. Student Dashboard — single student personal analytics
# ------------------------------------------------------------------

def get_student_dashboard_stats(student_id) -> dict:
    """
    Personal analytics for one student.

    DB queries: 3

    Args:
        student_id: UUID primary key of the target Student.

    Returns: {
        "overall": {
            "total_submissions": int,
            "marked_submissions": int,
            "scout_count": int,    "scout_avg_score": Decimal | None,
            "explorer_count": int, "explorer_avg_score": Decimal | None,
            "legend_count": int,   "legend_avg_score": Decimal | None,
        },
        "per_grade": [
            {
                "grade": str,
                "total_submissions": int,
                "overall_avg_score": Decimal | None,
                "scout_count": int,    "scout_avg_score": Decimal | None,
                "explorer_count": int, "explorer_avg_score": Decimal | None,
                "legend_count": int,   "legend_avg_score": Decimal | None,
            },
            ...  ordered by grade asc
        ],
        "per_subject": [
            {
                "subject_name": str,
                "subject_tag_name": str,
                "grade": str,
                "total_submissions": int,
                "avg_score": Decimal | None,
                "scout_count": int,
                "explorer_count": int,
                "legend_count": int,
            },
            ...  ordered by subject_name, grade asc
        ],
    }
    """
    # Single base queryset — student filter applied once, shared across all 3 queries
    base_qs = ExamSubmission.objects.filter(student_id=student_id).select_related(
        "exam__subject_tag__subject",
        "result",
    )

    # Q1 — Overall summary (.aggregate → no GROUP BY, one DB round-trip)
    overall_raw = base_qs.aggregate(
        total_submissions=Count("id"),
        marked_submissions=Count("id", filter=Q(is_marked=True)),
        **LEVEL_COUNT_ANNOTATIONS,
        **LEVEL_AVG_ANNOTATIONS,
    )

    overall = {
        "total_submissions": overall_raw["total_submissions"],
        "marked_submissions": overall_raw["marked_submissions"],
        "scout_count": overall_raw["scout_count"],
        "scout_avg_score": overall_raw["scout_avg_score"],
        "explorer_count": overall_raw["explorer_count"],
        "explorer_avg_score": overall_raw["explorer_avg_score"],
        "legend_count": overall_raw["legend_count"],
        "legend_avg_score": overall_raw["legend_avg_score"],
    }

    # Q2 — Per-grade breakdown (GROUP BY exam__grade)
    per_grade_qs = (
        base_qs
        .values("exam__grade")
        .annotate(
            total_submissions=Count("id"),
            **OVERALL_AVG_ANNOTATION,
            **LEVEL_COUNT_ANNOTATIONS,
            **LEVEL_AVG_ANNOTATIONS,
        )
        .order_by("exam__grade")
    )

    per_grade = [
        {
            "grade": row["exam__grade"],
            "total_submissions": row["total_submissions"],
            "overall_avg_score": row["overall_avg_score"],
            "scout_count": row["scout_count"],
            "scout_avg_score": row["scout_avg_score"],
            "explorer_count": row["explorer_count"],
            "explorer_avg_score": row["explorer_avg_score"],
            "legend_count": row["legend_count"],
            "legend_avg_score": row["legend_avg_score"],
        }
        for row in per_grade_qs
    ]

    # Q3 — Per subject-tag × grade (GROUP BY subject_tag + grade)
    # Q3 — Per subject-tag × grade
    per_subject_qs = (
        base_qs
        .values(
            subject_name=F("exam__subject_tag__subject__name"),
            subject_tag_name=F("exam__subject_tag__name"),
            grade=F("exam__grade"),
        )
        .annotate(
            total_submissions=Count("id"),
            avg_score=Round(
                Avg(
                    ExpressionWrapper(
                        F("result__score") / F("result__out_of") * 100,
                        output_field=FloatField(),
                    ),
                    filter=Q(result__isnull=False, result__out_of__gt=0),
                ),
                2,
            ),
            **LEVEL_COUNT_ANNOTATIONS,
        )
        .order_by("subject_name", "grade")
    )

    per_subject = [
        {
            "subject_name": row["subject_name"],
            "subject_tag_name": row["subject_tag_name"],
            "grade": row["grade"],
            "total_submissions": row["total_submissions"],
            "avg_score": row["avg_score"],
            "scout_count": row["scout_count"],
            "explorer_count": row["explorer_count"],
            "legend_count": row["legend_count"],
        }
        for row in per_subject_qs
    ]

    return {
        "overall": overall,
        "per_grade": per_grade,
        "per_subject": per_subject,
    }


# ============================================================
# analytics/serializers.py
# ============================================================

from rest_framework import serializers


# ---- Teacher serializers ----

class LevelDistributionSerializer(serializers.Serializer):
    total_submissions = serializers.IntegerField()
    unique_students = serializers.IntegerField()


class PerGradeTeacherSerializer(serializers.Serializer):
    grade = serializers.CharField()
    total_submissions = serializers.IntegerField()
    unique_students = serializers.IntegerField()
    scout_count = serializers.IntegerField()
    explorer_count = serializers.IntegerField()
    legend_count = serializers.IntegerField()


class SubjectDistributionSerializer(serializers.Serializer):
    subject_name = serializers.CharField()
    subject_tag_name = serializers.CharField()
    total_submissions = serializers.IntegerField()
    scout_count = serializers.IntegerField()
    explorer_count = serializers.IntegerField()
    legend_count = serializers.IntegerField()
    overall_avg_score = serializers.DecimalField(
        max_digits=6, decimal_places=2, allow_null=True
    )


class TopStudentSerializer(serializers.Serializer):
    student_id = serializers.UUIDField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    total_submissions = serializers.IntegerField()
    marked_submissions = serializers.IntegerField()
    overall_avg_score = serializers.DecimalField(
        max_digits=6, decimal_places=2, allow_null=True
    )


class TeacherDashboardSerializer(serializers.Serializer):
    level_distribution = serializers.DictField(child=LevelDistributionSerializer())
    per_grade = PerGradeTeacherSerializer(many=True)
    subject_distribution = SubjectDistributionSerializer(many=True)
    top_students = TopStudentSerializer(many=True)


# ---- Student serializers ----

class StudentOverallSerializer(serializers.Serializer):
    total_submissions = serializers.IntegerField()
    marked_submissions = serializers.IntegerField()
    scout_count = serializers.IntegerField()
    scout_avg_score = serializers.DecimalField(
        max_digits=6, decimal_places=2, allow_null=True
    )
    explorer_count = serializers.IntegerField()
    explorer_avg_score = serializers.DecimalField(
        max_digits=6, decimal_places=2, allow_null=True
    )
    legend_count = serializers.IntegerField()
    legend_avg_score = serializers.DecimalField(
        max_digits=6, decimal_places=2, allow_null=True
    )


class PerGradeStudentSerializer(serializers.Serializer):
    grade = serializers.CharField()
    total_submissions = serializers.IntegerField()
    overall_avg_score = serializers.DecimalField(
        max_digits=6, decimal_places=2, allow_null=True
    )
    scout_count = serializers.IntegerField()
    scout_avg_score = serializers.DecimalField(
        max_digits=6, decimal_places=2, allow_null=True
    )
    explorer_count = serializers.IntegerField()
    explorer_avg_score = serializers.DecimalField(
        max_digits=6, decimal_places=2, allow_null=True
    )
    legend_count = serializers.IntegerField()
    legend_avg_score = serializers.DecimalField(
        max_digits=6, decimal_places=2, allow_null=True
    )


class PerSubjectStudentSerializer(serializers.Serializer):
    subject_name = serializers.CharField()
    subject_tag_name = serializers.CharField()
    grade = serializers.CharField()
    total_submissions = serializers.IntegerField()
    avg_score = serializers.DecimalField(
        max_digits=6, decimal_places=2, allow_null=True
    )
    scout_count = serializers.IntegerField()
    explorer_count = serializers.IntegerField()
    legend_count = serializers.IntegerField()


class StudentDashboardSerializer(serializers.Serializer):
    overall = StudentOverallSerializer()
    per_grade = PerGradeStudentSerializer(many=True)
    per_subject = PerSubjectStudentSerializer(many=True)


# ============================================================
# analytics/views.py
# ============================================================

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response


class TeacherDashboardStatsView(GenericAPIView):
    """
    GET /api/v1/dashboard/teacher/stats/
    GET /api/v1/dashboard/teacher/stats/?grade=grade_3

    System-wide exam submission analytics.

    Query params:
        grade (optional) — one of ExamQuestion.GradeChoices values.
    """

    serializer_class = TeacherDashboardSerializer

    def _validate_grade(self, request: Request) -> tuple:
        """Return (grade, None) on success or (None, 400 Response) on bad input."""
        grade = request.query_params.get("grade")
        if grade and grade not in ExamQuestion.GradeChoices.values:
            return None, Response(
                {
                    "error": "Invalid grade.",
                    "valid_choices": list(ExamQuestion.GradeChoices.values),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return grade, None

    def get(self, request: Request) -> Response:
        grade, error = self._validate_grade(request)
        if error:
            return error

        data = get_teacher_dashboard_stats(grade=grade)
        serializer = self.get_serializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentDashboardStatsView(GenericAPIView):
    """
    GET /api/v1/dashboard/student/<student_id>/stats/

    Personal analytics for a single student.

    URL kwargs:
        student_id — UUID primary key of the Student record.
    """

    serializer_class = StudentDashboardSerializer

    def _get_student(self, student_id) -> tuple:
        """Return (student, None) or (None, 404 Response)."""
        try:
            # .only("id") — existence check only, no unnecessary column fetches
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

        data = get_student_dashboard_stats(student_id=student.id)
        serializer = self.get_serializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

