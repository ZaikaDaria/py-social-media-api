from django.urls import path, include
from rest_framework import routers

from social.views import HashtagViewSet, PostViewSet, ProfileViewSet

router = routers.DefaultRouter()
router.register("hashtags", HashtagViewSet)
router.register("posts", PostViewSet)
router.register("profiles", ProfileViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "social"
