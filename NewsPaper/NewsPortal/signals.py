from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Post, PostCategory


@receiver(post_save, sender=Post)
def notify_post_created(sender, instance, created, **kwargs):
    if created:
        pass

