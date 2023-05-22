# -*- coding: utf-8 -*-
from django import forms
from .models import Additional_User_Info,AI_Coursework, PE_Coursework, HDL_Coursework
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget

from django.contrib.auth.models import User

from django import forms

Auth_meth = [
    ('FIDO', 'FIDO'),
    ('OTP', 'OTP'),
    ('Password', 'Password'),
]


class edit_Submission(forms.Form):
    CHOICES = [
        ('option1', 'Yes'),
        ('option2', 'No'),
    ]
    choice_field = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
    docfile_group = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes',
        widget=forms.FileInput(attrs={'style': 'display:none;'}),
        
    )

class GradeForm(forms.Form):
   
    grade = forms.IntegerField(required=False)


        
class LeaderForm(forms.Form):
    CHOICES = [
        ('option1', 'Yes'),
        ('option2', 'No'),
    ]

    choice_field = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
    leader_username = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Enter his username', 'class': 'form-control', 'style': 'display:none;'}))

class UploadForm_Individual(forms.Form):
    docfile_individual = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )
 

class UploadForm_Group(forms.Form): 
    docfile_group = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )

class AI_CourseworkForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AI_CourseworkForm, self).__init__(*args, **kwargs)

    class Meta:
        model = AI_Coursework
        fields = ['Title', 'Submission_Date', 'Type']
        widgets = {
            'Submission_Date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

    def save(self, commit=True):
        instance = super(AI_CourseworkForm, self).save(commit=False)
        if self.user:
            instance.user = self.user
        if commit:
            instance.save()
        return instance
    
class PE_CourseworkForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PE_CourseworkForm, self).__init__(*args, **kwargs)

    class Meta:
        model = PE_Coursework
        fields = ['Title', 'Submission_Date', 'Type']
        widgets = {
            'Submission_Date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

    def save(self, commit=True):
        instance = super(PE_CourseworkForm, self).save(commit=False)
        if self.user:
            instance.user = self.user
        if commit:
            instance.save()
        return instance
    
class HDL_CourseworkForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(HDL_CourseworkForm, self).__init__(*args, **kwargs)

    class Meta:
        model = HDL_Coursework
        fields = ['Title', 'Submission_Date', 'Type']
        widgets = {
            'Submission_Date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

    def save(self, commit=True):
        instance = super(HDL_CourseworkForm, self).save(commit=False)
        if self.user:
            instance.user = self.user
        if commit:
            instance.save()
        return instance


class AddtionalInfoForm(forms.ModelForm):
    # role = forms.MultipleChoiceField(choices=Additional_User_Info.Roles)
    number= forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "+601234567890",
                "class": "form-control"
            }
        ))
    extension= forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "+60",
                "class": "form-control"
            }
        ))
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AddtionalInfoForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Additional_User_Info
        fields= ('role','number','default_authentication_method','multi_factor_authentication_method', 'extension', 'module_convenor')
        widgets = {
            'number': PhoneNumberInternationalFallbackWidget()
            
        }
    
    def clean(self):
        cleaned_data = super().clean()
        role = self.cleaned_data['role']
        module = self.cleaned_data['module_convenor']
        multi_auth = self.cleaned_data['multi_factor_authentication_method']
        number = self.cleaned_data['number']
        
        if role == "Lecturer":
            if multi_auth == []:

                self.errors['multi_factor_authentication_method'] = ['Lecturer must enable multi factor authentication method!']
                
            if module == None:
                self.errors['module'] = ['Please select a module!']
       
        return cleaned_data


    def save(self, commit=True):
        instance = super(AddtionalInfoForm, self).save(commit=False)
        if self.user:
            instance.user = self.user
        if commit:
            instance.save()
        return instance
    
class update_AddtionalInfoForm(forms.ModelForm):
    
    # Please include 'role' in the fields for easy switching roles

    #fields= ('number','default_authentication_method','multi_factor_authentication_method', 'extension', 'module_convenor')
    class Meta:
        model = Additional_User_Info
        fields= ('number','default_authentication_method','multi_factor_authentication_method', 'extension', 'module_convenor')
        widgets = {
            'number': PhoneNumberInternationalFallbackWidget(),
        }


class AddtionalInfoWithUserForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())
    user_info = AddtionalInfoForm()

    def __init__(self, *args, **kwargs):
        super(AddtionalInfoWithUserForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            self.fields['user'].initial = kwargs['instance'].user

    def save(self):
        user = self.cleaned_data['user']
        user_info = self.cleaned_data['user_info']
        user_info.user = user
        user_info.save()
        return user_info