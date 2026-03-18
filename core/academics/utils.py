from datetime import date

from django.utils.timezone import now
from rest_framework.exceptions import PermissionDenied


def get_current_day(enrollment):
    if not enrollment.start_date:
        return 1

    delta = (date.today() - enrollment.start_date).days + 1
    return min(delta, enrollment.challenge.duration_days)


def validate_day_access(enrollment, day_number):
    current_day = get_current_day(enrollment)

    if day_number > current_day:
        raise PermissionDenied("This day is locked")

    return True


def update_challenge_completion(enrollment):
    from .models import ChallengeDayProgress

    total_days = enrollment.challenge.duration_days

    completed_days = ChallengeDayProgress.objects.filter(
        enrollment=enrollment,
        is_completed=True
    ).count()

    if completed_days == total_days:
        enrollment.status = "completed"
        enrollment.save()


def update_day_progress(enrollment, day):
    from .models import ChallengeSubmission, ChallengeAssignment, ChallengeDayProgress

    # Get all assignments for this day
    assignments = ChallengeAssignment.objects.filter(day=day)
    total = assignments.count()

    # Count submissions for this enrollment
    submitted = ChallengeSubmission.objects.filter(
        assignment__in=assignments,
        enrollment=enrollment
    ).count()

    if total == 0:
        return  # No assignments, nothing to track

    # If all assignments are submitted, mark the day complete
    if total == submitted:
        progress, created = ChallengeDayProgress.objects.get_or_create(
            enrollment=enrollment,
            day=day
        )

        if not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = now()
            progress.save()

            # 🔹 Update current_day in enrollment
            if day.day_number >= enrollment.current_day:
                # Move to next day but do not exceed challenge duration
                enrollment.current_day = min(day.day_number + 1, enrollment.challenge.duration_days)
                enrollment.save()

        # 🔹 Check if the entire challenge is completed
        update_challenge_completion(enrollment)

