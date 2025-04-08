from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    email = forms.EmailField(label='Email', required=True)
    tekken_id = forms.CharField(label='Tekken ID', required=True)

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2', 'tekken_id']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']  # Use email as username
        if commit:
            user.save()
        return user