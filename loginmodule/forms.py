from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate


from .models import User

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=255, help_text="Required. Add a Valid email")
    name  = forms.CharField(max_length=20)
    class Meta:
        model = User
        fields = ('email', 'username','name', 'password1', 'password2')


    def clean_email(self):
        email = self.cleaned_data['email'].lower()

        try:
            user = User.objects.get(email=email)
        except Exception:
            return email
        raise forms.ValidationError(f"Email {email} is already in use")


    def clean_username(self):
        username = self.cleaned_data['username']

        try:
            user = User.objects.get(username=username)
        except Exception:
            return username
        raise forms.ValidationError(f"username {username} is already in use")


class AccountAuthenticationForm(forms.ModelForm):
    password = forms.CharField(label="password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email", "password")

    def clean(self):

        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']

            if not authenticate(email=email,password=password):
                raise forms.ValidationError("Invalid Login")