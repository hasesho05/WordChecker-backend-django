from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from . import views


urlpatterns = [
    path("admin", admin.site.urls),
    path("api/", include("app.urls")),
    re_path("static/*", views.static, name="static"),
    re_path(r"^alb/health_check$", lambda request: HttpResponse()),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),  # 追加
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),  # 追加
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
