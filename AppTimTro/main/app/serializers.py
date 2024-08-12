from rest_framework import serializers
from .models import Category, PropertyLandlord, PropertyImage, PropertyTenant, User, Follow, Comment


class UserSerializer(serializers.ModelSerializer):
    # Trường mới để tải lên avatar, không hiển thị trong phản hồi API (write_only=True)
    upload_avatar = serializers.ImageField(write_only=True, required=False)
    # SerializerMethodField để trả lại URL avatar
    avatar = serializers.SerializerMethodField()

    def get_avatar(self, User):
        request = self.context.get('request')
        if User.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri('/static/%s' % User.avatar.name)
            return '/static/%s' % User.avatar.name

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'avatar', 'upload_avatar', 'role',
                  'birth_date', 'address']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        avatar_data = validated_data.pop('upload_avatar', None)
        user = User.objects.create_user(**validated_data)
        if avatar_data:
            user.avatar = avatar_data
        user.set_password(validated_data['password'])
        user.save()
        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class PropertyImageSerializer(serializers.ModelSerializer):
    def get_image(self, PropertyImage):
        request = self.context.get('request')
        if PropertyImage.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri('/static/%s' % PropertyImage.image.name)
            return '/static/%s' % PropertyImage.image.name

    class Meta:

        model = PropertyImage
        fields = ['id', 'image', 'caption']


class PropertyLandlordSerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    user_landlord = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role=User.UserRole.LANDLORD))

    class Meta:
        model = PropertyLandlord
        fields = ['id', 'title', 'description', 'price', 'category', 'user_landlord', 'address', 'images']
        read_only_fields = ['is_approved']

    def create(self, validated_data):
        images_data = validated_data.pop('images',[])
        if len(images_data) < 3:
            raise serializers.ValidationError("Phải cung cấp tối thiểu 3 hình ảnh.")
        property_instance = PropertyLandlord.objects.create(**validated_data)
        for image_data in images_data:
            PropertyImage.objects.create(property=property_instance, **image_data)
        return property_instance


class PropertyTenantSerializer(serializers.ModelSerializer):
    user_tenant = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role=User.UserRole.TENANT))

    class Meta:
        model = PropertyTenant
        fields = ['id', 'title', 'description', 'price', 'category', 'area', 'user_tenant']

    def create(self, validated_data):
        return PropertyTenant.objects.create(**validated_data)


class FollowSerializer(serializers.ModelSerializer):
    landlord = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role=User.UserRole.LANDLORD))
    tenant = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role=User.UserRole.TENANT))

    class Meta:
        model = Follow
        fields = ['id', 'landlord', 'tenant']


class CommentSerializer(serializers.ModelSerializer):
    user_comment = UserSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'user', 'property', 'content', 'parent_cmt', 'created_date']


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyTenant
        fields = ['participant1', 'participant2', 'messages']
