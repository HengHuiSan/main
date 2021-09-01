from ctypes import addressof
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import fields
from ecommerce.models import *
from django.contrib.auth import authenticate


class UserRegistrationForm(UserCreationForm):
	# email = forms.EmailField(required=True)

	def clean_email(self):
		if User.objects.filter(email=self.cleaned_data['email']).exists():
			raise forms.ValidationError("Email is already in use.")
		return self.cleaned_data['email']

	def clean_username(self):
		if User.objects.filter(username=self.cleaned_data['username']).exists():
			raise forms.ValidationError("Username is already in use.")
		return self.cleaned_data['username']

	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']
		

	

