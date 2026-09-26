from django.urls import path

from .views import CheckoutView,OrderListView,OrderDetailView,OrderStatusUpdateView

urlpatterns = [
    path('', OrderListView.as_view(),name='order-list'),
    path('<int:pk>/', OrderDetailView.as_view(),name='order-detial'),
    path('checkout/', CheckoutView.as_view(),name='checkout'),
    path('<int:pk>/status/', OrderStatusUpdateView.as_view(),name='order-status-update'),
    
]