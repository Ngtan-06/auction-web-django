from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from django import forms

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Thêm class 'form-control' vào tất cả các trường
        for field in self.visible_fields():
            field.field.widget.attrs.update({'class': 'form-control'})

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'role')

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
