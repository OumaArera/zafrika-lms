from rest_framework import serializers


class TeacherDashboardStatsSerializer(serializers.Serializer):
    total_students = serializers.IntegerField()
    total_groups = serializers.IntegerField()
    total_subjects = serializers.IntegerField()

    total_exam_submissions = serializers.IntegerField()
    total_exams_marked = serializers.IntegerField()
    total_exam_results = serializers.IntegerField()

    total_exercise_submissions = serializers.IntegerField()

    average_exam_score = serializers.FloatField()
    overall_exam_percentage = serializers.FloatField()