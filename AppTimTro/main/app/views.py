from django.db.models.functions import ExtractMonth, ExtractYear, ExtractQuarter
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .perms import IsAdminUser, IsTenantUser, IsLandlordUser, IsAdminOrReadOnly, IsOwnerOrReadOnly
from .models import Category, PropertyImage, PropertyTenant, PropertyLandlord, User, Chat, Follow
from .serializers import CategorySerializer, PropertyLandlordSerializer, \
    PropertyTenantSerializer, ChatSerializer, UserSerializer, FollowSerializer, CommentSerializer
from rest_framework.exceptions import PermissionDenied
from .paginators import PropertyTenantPaginator, PropertyLandlordPaginator
from . import serializers


class UserViewset(viewsets.ViewSet, generics.RetrieveAPIView, generics.CreateAPIView):

    queryset =User.objects.all()
    serializer_class = UserSerializer

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_permissions(self):
        if self.action == 'retrieve':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(methods=['get'], url_path='current_user', detail=False)
    def get_current_user(self, request):
        user = request.user
        return Response (serializers.UserSerializer(user).data)


class CategoryViewset(viewsets.ViewSet, generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class PropertyLandlordViewSet(viewsets.ModelViewSet):
    queryset = PropertyLandlord.objects.filter(is_approved=True)
    serializer_class = PropertyLandlordSerializer
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]
    pagination_class = PropertyLandlordPaginator

    def get_queryset(self):
        # Nếu người dùng là admin, họ có thể xem tất cả các bài đăng
        if self.request.user.is_staff:
            return PropertyLandlord.objects.all()
        # Nếu không phải admin, chỉ hiển thị các bài đăng đã được duyệt
        return PropertyLandlord.objects.filter(is_approved=True)

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.user_landlord != self.request.user:
            raise PermissionDenied("Bạn không có quyền cập nhật bài này.")
        serializer.save()

    def perform_create(self, serializer):
        serializer.save(user_landlord=self.request.user)

    def perform_destroy(self, instance):
        if instance.user_landlord != self.request.user:
            raise PermissionDenied("Bạn không có quyền xóa bài này.")
        instance.delete()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Lọc theo quận/huyện/thành phố
        city = request.query_params.get('city', None)
        if city:
            queryset = queryset.filter(city__icontains=city)

        # Lọc theo số lượng người ở
        num_people = request.query_params.get('num_people', None)
        if num_people:
            queryset = queryset.filter(num_people=num_people)

        # Lọc theo mức giá mong muốn
        min_price = request.query_params.get('min_price', None)
        max_price = request.query_params.get('max_price', None)
        if min_price and max_price:
            queryset = queryset.filter(price__range=(min_price, max_price))
        elif min_price:
            queryset = queryset.filter(price__gte=min_price)
        elif max_price:
            queryset = queryset.filter(price__lte=max_price)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        property_landlord = self.get_object()
        property_landlord.is_approved = True
        property_landlord.save()
        return Response({'status': 'Bài đăng đã được duyệt'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        property_landlord = self.get_object()
        property_landlord.is_approved = False
        property_landlord.save()
        return Response({'status': 'Bài đăng đã bị từ chối'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='add_comment')
    def add_comment(self, request, pk=None):
        property_landlord = self.get_object()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, property=property_landlord)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='get_comments')
    def get_comments(self, request, pk=None):
        property_landlord = self.get_object()
        comments = property_landlord.comments.filter(active=True)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class PropertyTenantViewSet(viewsets.ModelViewSet):
    queryset = PropertyTenant.objects.all()
    serializer_class = PropertyTenantSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PropertyTenantPaginator

    def perform_create(self, serializer):
        serializer.save(user_tenant=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user_tenant=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='add_comment')
    def add_comment(self, request, pk=None):
        property_tenant = self.get_object()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, property=property_tenant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='get_comments')
    def get_comments(self, request, pk=None):
        property_tenant = self.get_object()
        comments = property_tenant.comments.filter(active=True)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class FollowListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer


class ChatViewset(viewsets.ViewSet,generics.ListAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
