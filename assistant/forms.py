from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ('name', 'email', 'password1', 'password2')
    
    def clean_email(self):
        """Validate that the email is not already in use"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered. Please use a different email or log in.")
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("This email address is already registered. Please use a different email or log in.")
        return email
    
    def save(self, commit=True):
        # Generate a unique username based on email if needed
        email = self.cleaned_data['email']
        base_username = email.split('@')[0]  # Use part before @ as base username
        
        # Try the base username first
        username = base_username
        counter = 1
        
        # If username already exists, add a number until we find a unique one
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
            
        user = super().save(commit=False)
        user.username = username
        user.email = email
        user.first_name = self.cleaned_data['name']
        
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    remember_me = forms.BooleanField(required=False)
