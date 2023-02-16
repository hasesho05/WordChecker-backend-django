from django.urls import include, path
from rest_framework import routers
from app.views import *

router = routers.DefaultRouter()
router.register(r"auth", AuthenticateView, basename="auth")
router.register(r"accounts", AccountViewSet, basename="accounts")
router.register(r"history", HistoryViewSet, basename="history")
router.register(r"userpost", PostViewSet, basename="userpost")
router.register(r"like_post", LikePostViewSet, basename="like_post")

urlpatterns = [
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
