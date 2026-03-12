from django.db.models import Sum, Avg, F, FloatField, ExpressionWrapper
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import (Student, Group)
from ...academics.models import (Subject, ExamSubmission, ExerciseSubmission, ExamResult)
from ..serializers import TeacherDashboardStatsSerializer
from ..middleware import IsTeacherAdmin


class TeacherDashboardStatsView(APIView):

    permission_classes = [IsAuthenticated, IsTeacherAdmin]

    def get(self, request):

        # Core entity counts
        total_students = Student.objects.count()
        total_groups = Group.objects.count()
        total_subjects = Subject.objects.count()

        # Submission counts
        total_exam_submissions = ExamSubmission.objects.count()
        total_exams_marked = ExamSubmission.objects.filter(is_marked=True).count()
        total_exercise_submissions = ExerciseSubmission.objects.count()
        total_exam_results = ExamResult.objects.count()

        # Compute percentage for each result
        percentage_expression = ExpressionWrapper(
            (F("score") * 100.0) / F("out_of"),
            output_field=FloatField()
        )

        # Aggregations
        score_aggregation = ExamResult.objects.annotate(
            percentage=percentage_expression
        ).aggregate(
            total_score=Sum("score"),
            total_out_of=Sum("out_of"),
            average_percentage=Avg("percentage"),
        )

        total_score = score_aggregation["total_score"] or 0
        total_out_of = score_aggregation["total_out_of"] or 0
        average_percentage = score_aggregation["average_percentage"] or 0

        overall_percentage = 0
        if total_out_of > 0:
            overall_percentage = (total_score / total_out_of) * 100

        data = {
            "total_students": total_students,
            "total_groups": total_groups,
            "total_subjects": total_subjects,
            "total_exam_submissions": total_exam_submissions,
            "total_exams_marked": total_exams_marked,
            "total_exam_results": total_exam_results,
            "total_exercise_submissions": total_exercise_submissions,
            "average_exam_score": round(average_percentage, 2),
            "overall_exam_percentage": round(overall_percentage, 2),
        }

        serializer = TeacherDashboardStatsSerializer(data)
        return Response(serializer.data)