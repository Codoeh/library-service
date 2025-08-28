from enum import StrEnum

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse,
    OpenApiParameter
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import (
    ValidationError as DRFValidationError,
    ValidationError
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer
)
from library_service.permissions import IsAdminOrIfAuthenticatedReadOnly


class BorrowingActions(StrEnum):
    LIST = "list"
    RETRIEVE = "retrieve"
    CREATE = "create"
    RETURN_BOOK = "return_book"
    UPDATE = "update"
    PARTIAL_UPDATE = "partial_update"
    DESTROY = "destroy"

AUTHENTICATED_ACTIONS = {
    BorrowingActions.LIST,
    BorrowingActions.RETRIEVE,
    BorrowingActions.CREATE,
    BorrowingActions.RETURN_BOOK,
}
ADMIN_ACTIONS = {
    BorrowingActions.UPDATE,
    BorrowingActions.PARTIAL_UPDATE,
    BorrowingActions.DESTROY,
}


list_parameters = [
            OpenApiParameter(
                name="is_active",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filter borrowings by active status (true/false)",
            ),
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter borrowings by user id (admin only)"
            ),
        ]


@extend_schema_view(
    list=extend_schema(
        description="Get list of borrowings. "
                    "Admin can filter by user_id and is_active status.",
        responses=BorrowingSerializer(many=True),
        parameters=list_parameters,
    ),
    retrieve=extend_schema(
        description="Get a detailed information about single borrowing.",
        responses=BorrowingDetailSerializer(many=False),
    ),
    create=extend_schema(
        description="Create new borrowing.",
        responses=BorrowingSerializer,
    ),
    update=extend_schema(
        description="Update an existing borrowing (e.g., actual_return_date).",
        responses=BorrowingSerializer,
    ),
    destroy=extend_schema(
        description="Delete a borrowing.",
        responses=None,
    )
)
class BorrowingViewSet(ModelViewSet):

    def get_permissions(self):
        action = self.action
        if action in AUTHENTICATED_ACTIONS:
            return [IsAuthenticated()]
        elif action in ADMIN_ACTIONS:
            return [IsAdminUser()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Borrowing.objects.all().select_related("book", "user")
        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")

        if user.is_staff:
            if user_id:
                queryset = queryset.filter(user_id=user_id)
        else:
            queryset = queryset.filter(user=user)

        if is_active is not None:
            if is_active.lower() in ["true", "1"]:
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active.lower() in ["false", "0"]:
                queryset = queryset.filter(actual_return_date__isnull=False)

        return queryset

    @extend_schema(
        description="Return a borrowed book and generate payment.",
        responses={
            200: OpenApiResponse(
                description="Book returned successfully. Returns payment URL.",
                response=BorrowingSerializer,
            ),
            400: OpenApiResponse(
                description="If book has already been returned."
            )
        }
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAdminOrIfAuthenticatedReadOnly],
        url_path="return_book"
    )
    def return_book(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "Not allowed."},
                status=403
            )

        if borrowing.actual_return_date is not None:
            return Response(
                {"detail": "This borrowing has already been returned."},
                status=status.HTTP_400_BAD_REQUEST
            )

        requested_actual_date = request.data.get("actual_return_date")
        data = {
            "actual_return_date":
                requested_actual_date or timezone.now().date()
        }

        serializer = self.get_serializer(
            borrowing,
            data=data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except DjangoValidationError as e:
            raise DRFValidationError(e.message_dict or {"detail": e.messages})
        except ValidationError as e:
            raise DRFValidationError(
                e.detail if hasattr(e, "detail") else {"detail": e}
            )
        payment = serializer.context.get("created_payment")

        response_data = {"detail": "Book returned successfully."}
        if payment:
            response_data["payment_url"] = payment.session_url

        return Response(response_data, status=status.HTTP_200_OK)
