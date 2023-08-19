import os
import uuid
from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Hashtag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        unique=True,
    )
    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True)
    bio = models.TextField(blank=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    follow = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="follow_profile",
        blank=True,
    )

    def __str__(self):
        return self.first_name + " " + self.last_name


def post_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/posts/", filename)


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    hashtags = models.ManyToManyField(Hashtag, related_name="posts", blank=True)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="posts")
    image = models.ImageField(null=True, upload_to=post_image_file_path)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
