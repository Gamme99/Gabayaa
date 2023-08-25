from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
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
            case_insensitive_username_field = '{}__iexact'.format(
                UserModel.USERNAME_FIELD)
            print("trying somthing with case sens: ",
                  case_insensitive_username_field)
            print("user: ", username, ": Password: ", password)
            user = UserModel._default_manager.get(
                **{case_insensitive_username_field: username})
            print("trying somthing with user: ", user)
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
        else:
            print("user name exist")
            if user.check_password(password) and self.user_can_authenticate(user):
                print("its all good")
                return user
