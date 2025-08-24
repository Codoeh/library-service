from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiResponse
)
from rest_framework.authentication import BasicAuthentication
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from books.models import Book
from books.serializers import BookSerializer
from library_service.permissions import IsAdminOrReadOnly


@extend_schema_view(
    list=extend_schema(
        description="Get list of all books.",
        responses=OpenApiResponse(BookSerializer(many=True)),
    ),
    retrieve=extend_schema(
        description="Get details of a book.",
        responses=OpenApiResponse(BookSerializer),
    ),
    create=extend_schema(
        description="Create a new book.",
        responses=OpenApiResponse(BookSerializer),
    ),
    update=extend_schema(
        description="Update an existing book.",
        responses=OpenApiResponse(BookSerializer),
    ),
    destroy=extend_schema(
        description="Delete a book.",
        responses=None,
    )
)
class BookViewSet(ModelViewSet):
    serializer_class = BookSerializer
    queryset = Book.objects.all()
    permission_classes = (IsAdminOrReadOnly,)

    def get_authenticators(self):
        """
        Return authentication classes depending on action:
        - "retrieve": BasicAuthentication
        - other actions: JWTAuthentication
        """
        if getattr(self, "action", None) == "retrieve":
            return [BasicAuthentication(),]
        return [JWTAuthentication(),]
