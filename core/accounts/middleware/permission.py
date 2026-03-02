from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model

User = get_user_model()


class RolePermission(BasePermission):
    allowed_roles = []

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in self.allowed_roles
        )

class IsAdminOrFirstAdmin(BasePermission):
    """
    - If no admin exists → allow any request (bootstrap mode)
    - If at least one admin exists → require authenticated admin
    """

    def has_permission(self, request, view):
        admin_exists = User.objects.filter(role=User.Role.ADMIN).exists()

        # Bootstrap case → allow anyone
        if not admin_exists:
            return True

        # Normal case → require authenticated admin
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.role == User.Role.ADMIN

class IsAdmin(RolePermission):
    allowed_roles = ["admin", "teacher-admin"]



class IsTeacher(RolePermission):
    allowed_roles = ["teacher", "teacher-admin"]


class IsStudent(RolePermission):
    allowed_roles = ["student", "parent"]


class IsParent(RolePermission):
    allowed_roles = ["parent"]
    
class IsAllUsers(RolePermission):
    allowed_roles = ["student", "teacher", "admin", "teacher-admin", "parent"]

class IsTeacherAdmin(RolePermission):
    allowed_roles=["teacher-admin", "teacher", "admin",]