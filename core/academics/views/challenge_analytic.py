from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import *

from django.db.models import Count, Avg, Q


class ChallengeAnalyticsView(APIView):

    def get(self, request, challenge_id):

        challenge = Challenge.objects.get(id=challenge_id)

        enrollments = ChallengeEnrollment.objects.filter(
            challenge=challenge
        )

        total = enrollments.count()

        approved = enrollments.filter(status="approved").count()
        pending = enrollments.filter(status="pending").count()
        completed = enrollments.filter(status="completed").count()

        # average completion %
        progress_data = ChallengeDayProgress.objects.filter(
            enrollment__challenge=challenge,
            is_completed=True
        ).values("enrollment").annotate(
            completed_days=Count("id")
        )

        avg_progress = 0
        if progress_data.exists():
            avg_progress = sum(
                (p["completed_days"] / challenge.duration_days) * 100
                for p in progress_data
            ) / progress_data.count()

        return Response({
            "total_students": total,
            "approved": approved,
            "pending": pending,
            "completed": completed,
            "average_progress": avg_progress
        })