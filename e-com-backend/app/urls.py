from django.urls import path,include
from .views import ProductView,CartView,OrderView,RegisterView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'products',ProductView,basename='products')
router.register(r'cart',CartView,basename='cart')
router.register(r'order',OrderView,basename='order')

urlpatterns = [
    path('',include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
]

