# from django.db import models
# # from django.contrib.auth.models import AbstractUser
# # from phone_field import PhoneField
# from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager


# class MyAccountManager(BaseUserManager):

#     def creat_user(self, email, username, password=None):
#         if not email:
#             raise ValueError("Users must have an email address.")
#         if not username:
#             raise ValueError("Users must have an username.")
#         user = self.model(email=self.normalize_email(
#             email), username=username)
#         user.set_passwrod(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, username, password):
#         user = self.create_user(
#             email=self.normalize_email(email),
#             username=username,
#             password=password,
#         )
#         user.is_admin = True
#         user.is_staff = True
#         user.is_superuser = True
#         user.save(using=self._db)
#         return user


# class Customer(AbstractUser):
#     first_name = models.CharField(max_length=30)
#     last_name = models.CharField(max_length=30)
#     email = models.EmailField(unique=True)
#     phone_number = models.CharField(max_length=20, null=True)
#     street_address = models.CharField(max_length=20, null=True)
#     city = models.CharField(max_length=20, null=True)
#     state = models.CharField(max_length=20, null=True)
#     zip_code = models.CharField(max_length=10, null=True)
#     billing_address = models.CharField(max_length=20, null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     # Add a related_name argument to the user_permissions and groups field
#     groups = models.ManyToManyField(
#         Group, verbose_name='groups', blank=True, related_name='customer_set')
#     user_permissions = models.ManyToManyField(
#         Permission, verbose_name='user permissions', blank=True, related_name='customer_set')

#     objects = MyAccountManager()

#     def __str__(self):
#         return self.username
