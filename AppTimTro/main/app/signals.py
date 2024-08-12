from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import PropertyLandlord, Follow


@receiver(post_save, sender=PropertyLandlord)
def send_new_post_email(sender, instance, created, **kwargs):
    if created:
        landlord = instance.user_landlord
        followers = Follow.objects.filter(landlord=landlord)
        for follow in followers:
            subject = 'Bài đăng mới từ {}'.format(landlord.username)
            message = 'Người cho thuê {} vừa đăng một bài mới: "{}".\n\nNội dung: {}'.format(
                landlord.username, instance.title, instance.description)
            from_email = 'your_email@gmail.com'
            recipient_list = [follow.tenant.email]
            send_mail(subject, message, from_email, recipient_list)