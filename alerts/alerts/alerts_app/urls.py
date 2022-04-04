from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register("alerts", views.AlertViewSet, basename="alerts")
router.register("items", views.AlertItemViewSet, basename="items")

urlpatterns = [
    path("", include(router.urls)),
]
