from django.urls import path
from .views import ProductDetailView, ProductListCreateView,CategoryDetailView,CategoryListView,ProductImageCreateView,ProductImageDetailView

urlpatterns = [
    path('', ProductListCreateView.as_view(), name='name-list-create'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),

    path('categories/',CategoryListView.as_view(),name='category-list-view'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(),name='category-details'),

    path('<int:product_id>/images/', ProductImageCreateView.as_view(),name='product-image-create'),
    path('<int:product_id>/images/<int:pk>', ProductImageDetailView.as_view(), name='product-detail'),
    
]
