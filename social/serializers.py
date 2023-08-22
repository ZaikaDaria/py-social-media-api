from rest_framework import serializers

from social.models import Hashtag, Post, Profile


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ("id", "name")


class PostSerializer(serializers.ModelSerializer):
    hashtags = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(), many=False
    )

    class Meta:
        model = Post
        fields = ("id", "title", "content", "created_at", "hashtags", "user", "image")


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "image")


class ProfileSerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True, read_only=True)
    follow = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Profile.objects.all()
    )
    user = serializers.StringRelatedField(many=False)

    class Meta:
        model = Profile
        fields = (
            "id",
            "user",
            "first_name",
            "last_name",
            "bio",
            "follow",
            "posts",
        )
