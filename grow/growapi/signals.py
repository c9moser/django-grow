from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

try:
    from allauth.account.signals import user_signed_up
except ImportError:
    user_signed_up = None


def _real_signed_up_handler(request, user, **kwargs):
    user.groups.add(Group.objects.get_or_create(name='grow-member'))
    user.groups.add(Group.objects.get_or_create(name=f'grow-u{user.id}-friends'))
    user.groups.add(Group.objects.get_or_create(name=f'grow-u{user.id}-blocked'))


if user_signed_up:
    @receiver(user_signed_up)
    def signed_up_handler(request, user, **kwargs):
        _real_signed_up_handler(request, user, **kwargs)
else:
    @receiver(post_save, sender=get_user_model())
    def user_post_save_handler(sender, instance, created, **kwargs):
        if created:
            _real_signed_up_handler(None, instance)
