from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterUser(UserCreationForm):
    class Meta:
        model = User
        fields = ['firstname', 'lastname', 'email', 'password1', 'password2']

