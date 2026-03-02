from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from ..services import AuthService
from ..serializers import *
from ..middleware import IsAdmin, IsAdminOrFirstAdmin
from rest_framework.permissions import IsAuthenticated


class LoginView(TokenObtainPairView):
    permission_classes = []
    serializer_class = CustomTokenSerializer


class CreateAdminView(APIView):
    permission_classes = [IsAdminOrFirstAdmin]

    def post(self, request):
        user = AuthService.create_admin(request.data)
        return Response({"id": user.id})


class BlockUserView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, user_id):
        AuthService.block_user(user_id)
        return Response({"detail": "User blocked"})


class UnblockUserView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, user_id):
        AuthService.unblock_user(user_id)
        return Response({"detail": "User unblocked"})


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        AuthService.change_password(
            request.user,
            serializer.validated_data["old_password"],
            serializer.validated_data["new_password"],
        )

        return Response({"detail": "Password changed successfully"})