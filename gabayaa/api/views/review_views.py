from requests import Response
from rest_framework import viewsets
from dukkaana.models import Review
from ..serializers.review_serializers import ReviewSerializer
from ..permissions import IsStaffOrReadOnly

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
