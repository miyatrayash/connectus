from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class AccountManager(BaseUserManager):

    def create_user(self, email, username, name, password, **other_fields):

        if not email:
            raise ValueError(_('You must provide email'))
        if not username:
            raise ValueError(_('You must provide username'))
        print(email)
        email = self.normalize_email(email)
        user = self.model(email=email, username=username ,name=name, **other_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, name, password,**other_fields):

        other_fields.setdefault('is_staff',True)
        other_fields.setdefault('is_superuser',True)
        other_fields.setdefault('is_active',True)

        if other_fields.get('is_staff') is not True:
            raise ValueError("Super user must be assigned to is_staff=True")

        if other_fields.get('is_superuser') is not True:
            raise ValueError("Super user must be assigned to is_superuser=True")

        return self.create_user(email,username,name,password,**other_fields)



# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    email        = models.EmailField(_('email address'), unique=True,primary_key=True)
    username     = models.CharField(max_length=150,unique=True)
    name         = models.CharField(max_length=150)
    start_date   = models.DateTimeField(auto_now_add=True)
    last_login   = models.DateTimeField(auto_now=True)
    about        = models.TextField(_('about'), max_length=500,blank=True)
    friends      = models.ManyToManyField("self",blank=True,symmetrical=False,null=True,default=None)
    is_staff     = models.BooleanField(default=False)
    is_active    = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = AccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','name']

    def __str__(self) -> str:
        return self.username

    def has_perm(self, perm: str, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return True



