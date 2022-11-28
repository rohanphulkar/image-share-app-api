from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
class MyAccountManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have a password')

        user = self.model(
            email=self.normalize_email(email),
            # username=username,
        )

        user.set_password(password)

        # may have to add 'using=self._db' parameter.
        user.save()
        return user

    def create_superuser(self, email, password=None):
        if password is None:
            raise TypeError('Password should not be none')

        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            # username=username,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_verified = True
        user.save()
        return user


class Account(AbstractBaseUser):
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    can_reset_password = models.BooleanField(default=False)
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    # For checking permissions. to keep it simple all admin have ALL permissons
    def has_perm(self, perm, obj=None):
        return self.is_admin

    # Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
    def has_module_perms(self, app_label):
        return True

    def token(self):
        token = Token.objects.get_or_create(user=self)[0].key
        return {
            'token': token
        }
    
    


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

import string,random
generator = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))
from shortuuid.django_fields import ShortUUIDField

class SharedFile(models.Model):
    link=ShortUUIDField(length=7, max_length=11)
    file = models.FileField(upload_to='shared_files/')
    file_name = models.CharField(max_length=100, blank=True, null=True)
    file_size = models.CharField(max_length=100, blank=True, null=True)
    file_type = models.CharField(max_length=100, blank=True, null=True)
    owner = models.ForeignKey(Account, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    expires_on = models.DateTimeField(default=timezone.now() + timezone.timedelta(days=1))
    

    def __str__(self):
        return self.owner.email