from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0, blank=True)
    grad_year = models.IntegerField(default=0, blank=True)
    avatar = models.ImageField(upload_to='images/', blank=True)
    said_thanks = models.BooleanField(default=False)

    def __str__(self):  # __unicode__ for Python 2
        return self.user.username

# from django.contrib.auth.models import User
# user = User.objects.get(pk=1)
# user.profile.rating = 2
# user.save()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
