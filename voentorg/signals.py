from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Cart


@receiver(post_save, sender=CustomUser)
def create_user_cart(sender, instance, created, **kwargs):
    """Автоматически создает корзину при создании пользователя"""
    if created:
        Cart.objects.create(user=instance)


# В apps.py
from django.apps import AppConfig


class VoentorgConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'voentorg'

    def ready(self):
        import voentorg.signals