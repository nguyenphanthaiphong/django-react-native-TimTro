from django.db.models import Count
from django.template.response import TemplateResponse

from .models import Category, User, PropertyLandlord, \
    PropertyTenant, PropertyImage, Comment, Follow
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path


class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'id_user', 'first_name', 'last_name', 'role', 'avatar_image']
    search_fields = ['id_user', 'username', 'role']
    list_filter = ['role']

    # băm mk do băm bị lỗi
    def save_model(self, request, obj, form, change):
        if not change or 'password' in form.changed_data:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)

    def avatar_image(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="width: auto; height: 80px; object-fit: contain;" />',obj.avatar.url)
        else:
            return "No Image"

    avatar_image.short_description = 'Avatar'


class CategoryAdmin (admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    list_filter = ['id', 'name']


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1


class PropertyLandlordAdmin (admin.ModelAdmin):
    inlines = [PropertyImageInline]
    list_display = ['id', 'title', 'category', 'price', 'user_landlord']
    search_fields = ['id', 'address', 'price']


class PropertyTenantAdmin (admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'price', 'user_tenant']
    search_fields = ['id', 'area']


admin.site.register(User, UserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(PropertyLandlord, PropertyLandlordAdmin)
admin.site.register(PropertyTenant, PropertyTenantAdmin)
admin.site.register(Comment)
admin.site.register(Follow)
