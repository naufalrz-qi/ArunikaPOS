from django import forms
from django.contrib.auth.models import User
from .models import ServerConfig
from cryptography.fernet import Fernet
from django.conf import settings

class ServerConfigForm(forms.ModelForm):
    password_input = forms.CharField(
        widget=forms.PasswordInput(render_value=True),
        required=False,
        label="Password Database",
        help_text="Isi untuk mengubah password, biarkan kosong jika tidak berubah."
    )

    class Meta:
        model = ServerConfig
        fields = ['nama', 'tipe', 'host', 'port', 'db_name', 'username', 'is_active']
        widgets = {
            'tipe': forms.Select(choices=ServerConfig.SERVER_TYPES),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['password_input'].required = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        pwd = self.cleaned_data.get('password_input')
        if pwd:
            cipher_suite = Fernet(settings.SECRET_KEY_BYTES)
            encrypted_pwd = cipher_suite.encrypt(pwd.encode('utf-8'))
            instance.password = encrypted_pwd
        if commit:
            instance.save()
        return instance

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False, help_text="Isi untuk mereset password.")
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['password'].required = True

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
