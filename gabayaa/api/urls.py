from rest_framework.routers import DefaultRouter
from .views.product_views import ProductViewSet
from .views.review_views import ReviewViewSet
from .views.user_views import UserViewSet, RegisterUserView
from django.urls import path

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'user', UserViewSet)
router.register(r'review', ReviewViewSet)

urlpatterns = router.urls + [
    path('register/', RegisterUserView.as_view(), name='register-user'),
]
