from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class UserRole(models.TextChoices):
        ADMIN = 'admin'
        LANDLORD = 'landlord'
        TENANT = 'tenant'

    role = models.CharField(max_length=10, choices=UserRole, default=UserRole.TENANT)
    email = models.EmailField(("email address"), blank=False, null=False)
    id_user = models.IntegerField(unique=False, blank=True, null=True)
    birth_date = models.DateField(null=True)
    address = models.CharField(max_length=128)
    avatar = models.ImageField(upload_to='avatarUser/%Y/%m', null=False, blank=False)
    phone = models.CharField(max_length=15)

    def save(self, *args, **kwargs):
        if self._state.adding and self.id_user is None:
            count = User.objects.filter(role=self.role).count()
            self.id_user = count + 1
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.first_name + " " + self.last_name


# class truu tuong
class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Property(BaseModel):
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class PropertyLandlord(Property):
    address = models.CharField(max_length=225, null=False, blank=False)
    user_landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='landlord_properties',
                                      limit_choices_to={'role': User.UserRole.LANDLORD})
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title}, {self.user_landlord}"


class PropertyImage(models.Model):
    property = models.ForeignKey(PropertyLandlord, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='imageTimTro/%Y/%m')
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.caption or f"Image for {self.property}"


class PropertyTenant(Property):
    area = models.CharField(max_length=50, null=False, blank=False)
    user_tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tenant_properties',
                                    limit_choices_to={'role': User.UserRole.TENANT})

    def __str__(self):
        return f"{self.title}, {self.user_tenant}"


class Comment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(PropertyLandlord, on_delete=models.CASCADE)
    content = models.TextField()
    parent_cmt = models.ForeignKey("Comment", null=True, blank=True, related_name="replies", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user) + " " + self.content


class Follow(models.Model):
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed_by_tenants',
                                 limit_choices_to={'role': User.UserRole.LANDLORD})
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follows_landlords',
                               limit_choices_to={'role': User.UserRole.TENANT})

    class Meta:
        unique_together = ('tenant', 'landlord')


class Chat(models.Model):
    participant1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participant1_chats')
    participant2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participant2_chats')
    messages = models.JSONField(default=list)

    def __str__(self):
        return f"Chat between {self.participant1.first_name} and {self.participant2.first_name}"
