from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
# from django.contrib.auth.base_user import AbstractBaseUser
# from django.http.request import HttpRequest


class CaseInsensitiveModelBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            print("user name is none")
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            print("cant beleive am here")
            # Try username or email (case-insensitive)
            user = UserModel._default_manager.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
            print("trying somthing with user: ", user)
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
        else:
            print("user name exist")
            if user.check_password(password) and self.user_can_authenticate(user):
                print("its all good")
                return user
