from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from statistics_operator.views import *

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customers')
router.register(r'purchases', PurchaseViewSet, basename='purchases')
router.register(r'summary', PurchaseSummaryView, basename='summary')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
