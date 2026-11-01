from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import StudentProfile


class StudentSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=40)
    last_name = forms.CharField(max_length=40, required=False)
    email = forms.EmailField()
    roll_no = forms.CharField(max_length=20)
    department = forms.CharField(max_length=80)
    phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def clean_roll_no(self):
        roll = self.cleaned_data["roll_no"].strip().upper()
        if StudentProfile.objects.filter(roll_no=roll).exists():
            raise forms.ValidationError("This roll number is already registered.")
        return roll

    def save(self, commit=True):
        user = super().save(commit=commit)
        StudentProfile.objects.create(
            user=user,
            roll_no=self.cleaned_data["roll_no"],
            department=self.cleaned_data["department"],
            phone=self.cleaned_data["phone"],
        )
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ("department", "phone")
