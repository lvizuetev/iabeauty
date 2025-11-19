from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Empleado, Comment

class UserEmpleadoRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    nombre = forms.CharField(max_length=50)
    apellido = forms.CharField(max_length=50)
    identificacion = forms.CharField(max_length=50)
    edad = forms.IntegerField()
    telefono = forms.CharField(max_length=10)
    direccion = forms.CharField(max_length=50)
    foto = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username','nombre', 'apellido', 'identificacion', 'edad', 'telefono', 'direccion', 'email', 'password1', 'password2', 'foto']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            empleado = Empleado(
                user=user,
                nombre=self.cleaned_data['nombre'],
                apellido=self.cleaned_data['apellido'],
                identificacion=self.cleaned_data['identificacion'],
                edad=self.cleaned_data['edad'],
                email=self.cleaned_data['email'],
                telefono=self.cleaned_data['telefono'],
                direccion=self.cleaned_data['direccion'],
                foto=self.cleaned_data['foto']
            )
            empleado.save()
        return user

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Username', max_length=254)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class EmpleadoUpdateForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['nombre', 'apellido', 'identificacion', 'edad', 'email', 'telefono', 'direccion', 'foto']

    def __init__(self, *args, **kwargs):
        super(EmpleadoUpdateForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].disabled = True
        self.fields['apellido'].disabled = True
        self.fields['identificacion'].disabled = True
        self.fields['edad'].disabled = True
        self.fields['direccion'].disabled = True

class CreateCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['nombre', 'email', 'comentario']