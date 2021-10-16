from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

from account.utils import genOtp


class UserManager(BaseUserManager):
    def create_user(self, mobile_number, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not mobile_number:
            raise ValueError('Users must have an email address')

        user = self.model(
            mobile_number=mobile_number,
            email=self.normalize_email(email)
        )
        user.is_active = False
        user.set_password(password)
        user.save(using=self._db)
        return user



    def create_superuser(self,mobile_number, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """

        user = self.create_user(
            mobile_number=mobile_number,
            email=email,
            password=password,
        )
        user.is_active = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    gender_choices = (('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other'))
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    mobile_number = models.CharField(max_length=200, unique=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200, blank=True, null=True)
    gender = models.CharField(choices=gender_choices, max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_professor = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)



    objects = UserManager()

    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = ['email']



    def __str__(self):
        return self.email


    def get_full_name(self):
        # The user is identified by their email address
        return self.first_name + self.last_name
    @property
    def phone_number(self):
        return str(self.mobile_number)

    def __str__(self):              # __unicode__ on Python 2
        return str(self.mobile_number)


    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

from django.contrib.auth import  get_user_model

class UserOtp(models.Model):
    user = models.OneToOneField(get_user_model(),on_delete=models.CASCADE,blank=True,null=True)
    otp = models.CharField(max_length=10,default=genOtp())
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)
