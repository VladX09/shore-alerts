from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register(r"snippets", views.AlertViewSet, basename="alerts")

urlpatterns = [
    path("", include(router.urls)),
]
