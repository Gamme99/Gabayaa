from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.views import APIView
from dukkaana.models import Customer as User
from ..serializers.user_serializers import UserSerializer, RegisterUserSerializer
from ..permissions import IsManager


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsManager]
    # print(queryset)


class RegisterUserView(APIView):
    permission_classes = [IsManager]
    serializer_class = RegisterUserSerializer

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User registered successfully!', 'user_id': user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
