from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register("students", StudentViewSet)
router.register("teachers", TeacherViewSet)
router.register("parents", ParentViewSet)
router.register("users", UserViewSet)
router.register(r"groups", GroupViewSet, basename="groups")
router.register(r"virtual-classes", VirtualClassViewSet, basename="virtual-classes")
router.register(r"subscriptions", SubscriptionViewSet, basename="subscriptions")
router.register(r"subscription-plans", SubscriptionPlanViewSet, basename="subscription-plans")

urlpatterns = [
    path("auth/login/", LoginView.as_view()),
    path("auth/token/refresh/", TokenRefreshView.as_view()),
    path("auth/change-password/", ChangePasswordView.as_view()),
    path("auth/create-admin/", CreateAdminView.as_view()),
    path("auth/block/<uuid:user_id>/", BlockUserView.as_view()),
    path("auth/unblock/<uuid:user_id>/", UnblockUserView.as_view()),
    path("teacher/dashboard/stats/", TeacherDashboardStatsView.as_view()),
    path("plan-stats/", PlanStatsView.as_view(), name="plan-stats"),
] + router.urls