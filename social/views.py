from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from social.models import Hashtag, Post, Profile
from social.permissions import IsAuthorOrReadOnly
from social.serializers import (
    HashtagSerializer,
    PostSerializer,
    PostImageSerializer,
    ProfileSerializer,
)
from user.models import User


class HashtagViewSet(viewsets.ModelViewSet):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.prefetch_related("hashtags")
    serializer_class = PostSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """Retrieve the posts with filter by hashtags"""
        hashtags = self.request.query_params.get("hashtags")

        queryset = self.queryset

        if hashtags:
            hashtags_ids = self._params_to_ints(hashtags)
            queryset = queryset.filter(hashtags__id__in=hashtags_ids)

        return queryset.select_related("user").distinct()

    def get_serializer_class(self):
        if self.action == "upload_image":
            return PostImageSerializer

        return PostSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAuthorOrReadOnly],
    )
    def upload_image(self, request, pk=None):
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Only for documentation
        @extend_schema(
            parameters=[
                OpenApiParameter(
                    "hashtags",
                    type=OpenApiTypes.INT,
                    description="Filter by hashtags id (ex. ?hashtags=1)",
                )
            ]
        )
        def list(self, request, *args, **kwargs):
            return super().list(request, *args, **kwargs)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    filter_backends = [filters.SearchFilter]
    search_fields = ["username", "email"]

    def perform_create(self, serializer):
        user = self.request.user
        profile, created = Profile.objects.get_or_create(user=user)
        if created:
            profile.first_name = serializer.validated_data.get("first_name")
            profile.last_name = serializer.validated_data.get("last_name")
            profile.bio = serializer.validated_data.get("bio")
            profile.email = serializer.validated_data.get("email")
            profile.follow.set(serializer.validated_data.get("follow", []))
            profile.save()
        serializer.instance = profile

    @action(
        methods=["POST"],
        detail=True,
        url_path="follow",
        permission_classes=[IsAuthenticated],
    )
    def follow_user(self, request, pk=None):
        profile = self.get_object()
        user_to_follow = get_object_or_404(User, pk=pk)

        profile.follow.add(user_to_follow)

        if request.user != user_to_follow:
            return Response(
                "User was followed successfully.",
                status=status.HTTP_200_OK,
            )
        return Response(
            "You cannot follow yourself.",
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        methods=["POST"],
        detail=True,
        url_path="unfollow",
        permission_classes=[IsAuthenticated],
    )
    def unfollow_user(self, request):
        """Endpoint for unfollowing a user."""
        profile = self.get_object()
        user = request.user

        profile.follow.remove(user)
        return Response(
            {"detail": "You have successfully unsubscribed from this profile."},
            status=status.HTTP_200_OK,
        )
