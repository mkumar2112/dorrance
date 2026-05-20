from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import User
from .serializers import UserSerializer


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from .serializers import LoginSerializer, RegisterSerializer



class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.filter(is_deleted=False)

        mobile_number = self.request.query_params.get("mobile_number")
        email = self.request.query_params.get("email")
        username = self.request.query_params.get("username")
        role = self.request.query_params.get("role")
        is_active = self.request.query_params.get("is_active")
        is_blocked = self.request.query_params.get("is_blocked")
        login_type = self.request.query_params.get("login_type")

        if mobile_number:
            queryset = queryset.filter(mobile_number__icontains=mobile_number)

        if email:
            queryset = queryset.filter(email__icontains=email)

        if username:
            queryset = queryset.filter(username__icontains=username)

        if role:
            queryset = queryset.filter(role_id=role)

        if login_type:
            queryset = queryset.filter(login_type=login_type)

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        if is_blocked is not None:
            queryset = queryset.filter(is_blocked=is_blocked.lower() == "true")

        return queryset.order_by("-id")

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_deleted = True
        user.is_active = False
        user.save(update_fields=["is_deleted", "is_active"])

        return Response(
            {
                "status": True,
                "message": "User deleted successfully."
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    def block(self, request, pk=None):
        user = self.get_object()
        reason = request.data.get("reason")

        user.block_user(reason)

        return Response({
            "status": True,
            "message": "User blocked successfully."
        })

    @action(detail=True, methods=["post"])
    def unblock(self, request, pk=None):
        user = self.get_object()
        user.unblock_user()

        return Response({
            "status": True,
            "message": "User unblocked successfully."
        })

    @action(detail=True, methods=["post"])
    def check_permission(self, request, pk=None):
        user = self.get_object()
        permission_slug = request.data.get("permission")

        if not permission_slug:
            return Response(
                {
                    "status": False,
                    "message": "Permission is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            "status": True,
            "permission": permission_slug,
            "has_permission": user.has_role_permission(permission_slug)
        })




class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]

            refresh = RefreshToken.for_user(user)

            user.last_login = timezone.now()
            user.last_login_ip = self.get_client_ip(request)
            user.last_login_device = request.META.get("HTTP_USER_AGENT", "")
            user.save(update_fields=[
                "last_login",
                "last_login_ip",
                "last_login_device"
            ])

            return Response({
                "success": True,
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "uuid": str(user.uuid),
                    "mobile_number": user.mobile_number,
                    "email": user.email,
                    "username": user.username,
                    "role": user.role.name if user.role else None,
                    "is_superuser": user.is_superuser,
                },
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                }
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "message": "Login failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")
    
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)

            return Response({
                "success": True,
                "message": "User registered successfully",
                "user": {
                    "id": user.id,
                    "uuid": str(user.uuid),
                    "mobile_number": user.mobile_number,
                    "email": user.email,
                    "username": user.username,
                    "role": user.role.slug if user.role else None,
                },
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                }
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Registration failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


