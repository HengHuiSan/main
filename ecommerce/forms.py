from crispy_forms.layout import Column, Layout, Row, Submit, Button
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import fields
from django.forms.models import ALL_FIELDS, ModelForm
from django.forms.widgets import DateInput
from ecommerce.models import *
from crispy_forms.helper import FormHelper



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
		

class DonationForm(forms.Form):
	firstname = forms.CharField(
		label="First Name",
		max_length=50,
		)
	lastname = forms.CharField(
		label="Last Name",
		max_length=50
		)
	type = forms.CharField(
		label="Item Type",
		max_length=20
		)
	description = forms.CharField(
		max_length=500, 
		required=False
		)
	image = forms.ImageField(
		required=False
	)
	year_purchased = forms.DateField(
		label="Year Purchased",
		widget=DateInput
		)
	original_price = forms.DecimalField(
		label="Original Price",
		max_digits=8, 
		decimal_places=2, 
		required=False
		)


class CustomFieldForm(DonationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('firstname', css_class='form-group col-md-6'),
                Column('lastname', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
			Row(Column('type'), css_class='form-group'),
			Row(Column('description'), css_class='form-group'),
			Row(Column('image'), css_class='form-group'),
            Row(
                Column('year_purchased', css_class='form-group col-md-6'),
                Column('original_price', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            # CustomCheckbox('check_me_out'),  # <-- Here
            Button('submit', 'Cancel', css_class='btn btn-primary mb-3'),
            Submit('submit', 'Submit', css_class='mb-3 mr-3'),
        )
	
class texting(ModelForm):
	class Meta:
		model = Image
		fields = ['img']