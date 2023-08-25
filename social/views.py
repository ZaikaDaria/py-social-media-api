from django.http import Http404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from social.models import Hashtag, Post, Profile, Comment, Like
from social.permissions import IsAuthorOrReadOnly
from social.serializers import (
    HashtagSerializer,
    PostSerializer,
    PostImageSerializer,
    ProfileSerializer,
    CommentSerializer,
    LikeSerializer,
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

        serializer.is_valid(raise_exception=True)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["POST"],
        detail=True,
        url_path="like",
        permission_classes=(IsAuthenticated,),
    )
    def likes(self, request, pk=None):
        post = self.get_object()
        user = self.request.user

        try:
            like = get_object_or_404(Like, post=post, user=user)
            like.delete()
        except Http404:
            Like.objects.create(post=post, user=user, is_liked=True)

        return Response(status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=True,
        url_path="add_comment",
        permission_classes=(IsAuthenticated,),
    )
    def add_comment(self, request, pk=None):
        post = self.get_object()
        user = self.request.user

        Comment.objects.create(post=post, user=user, content=request.data["content"])

        return Response(status=status.HTTP_200_OK)

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
            profile.follow_profiles.set(serializer.validated_data.get("follow", []))
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

        profile.follow_profiles.add(user_to_follow)

        if (
            profile != user_to_follow
            and user_to_follow not in profile.follow_profiles.all()
        ):
            profile.follow_profiles.add(user_to_follow)
            profile.save()
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

        profile.follow_profiles.remove(user)
        return Response(
            {"detail": "You have successfully unsubscribed from this profile."},
            status=status.HTTP_200_OK,
        )


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)

    def get_queryset(self):
        queryset = self.queryset.select_related("post")
        user = self.request.user

        queryset = queryset.filter(user=user)

        return queryset


class LikeViewSet(viewsets.ModelViewSetw):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
