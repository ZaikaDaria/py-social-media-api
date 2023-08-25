from rest_framework import routers

from social.views import (
    HashtagViewSet,
    PostViewSet,
    ProfileViewSet,
    CommentViewSet,
    LikeViewSet,
)

router = routers.DefaultRouter()
router.register("hashtags", HashtagViewSet)
router.register("posts", PostViewSet)
router.register("profiles", ProfileViewSet)
router.register("comments", CommentViewSet)
router.register("likes", LikeViewSet)

urlpatterns = router.urls

app_name = "social"
