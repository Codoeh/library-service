from drf_spectacular.utils import extend_schema
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateAPIView,
    ListAPIView
)
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.models import User
from user.serializers import UserSerializer


@extend_schema(
    description="Register a new user",
    request=UserSerializer,
    responses={201: UserSerializer}
)
class CreateUserView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny,]


@extend_schema(
    description="Get or update your own user profile",
    request=UserSerializer,
    responses={200: UserSerializer}
)
class ManageUserView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


@extend_schema(
    description="List of all users (Admin only)",
    responses={200: UserSerializer(many=True)}
)
class UserListView(ListAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminUser,)
    queryset = User.objects.all()
