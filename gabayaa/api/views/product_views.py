from requests import Response
from rest_framework import viewsets
from dukkaana.models import Product
from ..serializers.product_serializers import ProductSerializer
from ..permissions import IsStaffOrReadOnly

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsStaffOrReadOnly]

    # print(queryset)
