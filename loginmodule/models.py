from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class AccountManager(BaseUserManager):

    def create_user(self, email, username, name, password):

        if not email:
            raise ValueError(_('You must provide email'))
        if not username:
            raise ValueError(_('You must provide username'))
        print(email)
        email = self.normalize_email(email)
        user = self.model(email=email, username=username ,name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, name, password):

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            name=name
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)

        user.save(using=self._db)

        return user



def get_profile_image_filepath(self,filename):
    return f'img/profile_images/{self.pk}/profile_image.png'



def get_default_profile_image():
    return "img/default/Avatar_Dog.png"
class User(AbstractBaseUser, PermissionsMixin):
    id              = models.AutoField(primary_key=True)
    email           = models.EmailField(_('email address'), unique=True)
    username        = models.CharField(max_length=150,unique=True)
    name            = models.CharField(max_length=150)
    start_date      = models.DateTimeField(auto_now_add=True)
    last_login      = models.DateTimeField(auto_now=True)
    about           = models.TextField(_('about'), max_length=500,blank=True)
    is_staff        = models.BooleanField(default=False)
    profile_image   = models.ImageField(max_length=255, upload_to=get_profile_image_filepath, null=True,blank=True,default=get_default_profile_image)
    is_active       = models.BooleanField(default=True)
    is_superuser    = models.BooleanField(default=False)
    hide_email      = models.BooleanField(default=True)

    objects = AccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','name']

    def __str__(self) -> str:
        return self.username

    def has_perm(self, perm: str, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return True
