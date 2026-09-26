from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser

from .models import Product,Category,ProductImage
from .serializers import ProductSerializer,CategorySerializer,ProductImageSerializer
from .permissions import IsStaffOrReadOnly

# Create your views here.

class ProductImageCreateView(generics.CreateAPIView):
    serializer_class = ProductImageSerializer
    permission_classes = [IsStaffOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self,serializer):
        product =  get_object_or_404(
            Product,
            pk = self.kwargs['product_id']
        )
        serializer.save(product=product)
   
class ProductImageDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = ProductImageSerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_id'])

    def perform_destroy(self, instance):
        if instance.image:
            instance.image.delete(save=False)

        instance.delete()

class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsStaffOrReadOnly]

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsStaffOrReadOnly]


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    permission_classes = [IsStaffOrReadOnly]

    filterset_fields = ['category', 'is_active']
    search_fields = ['name','description']
    ordering_fields = ['price','created_at','name','stock']
    ordering = ['-created_at']

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset =Product.objects.select_related('category').all()
    serializer_class = ProductSerializer

