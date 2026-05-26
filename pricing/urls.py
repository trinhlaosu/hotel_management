from django.urls import include, path
from rest_framework.routers import DefaultRouter

from pricing.views import PricingViewSet


router = DefaultRouter(trailing_slash=True)
router.register('', PricingViewSet, basename='pricing')

urlpatterns = [
    path('', include(router.urls)),
]
