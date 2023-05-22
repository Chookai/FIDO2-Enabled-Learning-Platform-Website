from django.db import models
from django.contrib.auth.models import User
# Create your models here.

from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from phonenumber_field.widgets import PhoneNumberPrefixWidget
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField
import os
from uuid import uuid4
from functools import partial

Auth_meth= [
    ('Password', 'Password'),
    ('OTP', 'OTP'),
    
    ('FIDO', 'FIDO'),
    
    ]
Two_Factor_Auth_meth =[
    ('First', 'FIDO'),
    ('OTP', 'OTP'),
    ('Password', 'Password'),
]
Roles = [
    ('Lecturer', 'Lecturer'),
    ('Student','Student'),
]

Approval = [
    ('Required','Required'),
    ('Not Required',' Not Required'),
    {'Completed','Completed'}
]
Coursework_Type = [
    ('Individual','Individual'),
    ('Group','Group'),

]
modules= [
    ('AI','AI'),
    ('PE','PE'),
    ('HDL','HDL')
]
choice = [
    ('Yes','Yes'),
    ('No','No')

]
def rename_uploaded_file(instance,filename):


    return os.path.join(instance.__class__.__name__,instance.Coursework.Type,instance.Coursework.Title,filename)


class AI_Coursework(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="module_convenor",default='1')
    Title = models.CharField(max_length=50,null=True,default=None,blank=True)
    Submission_Date= models.DateTimeField(null=True,default=None,blank=True)
    Type = models.CharField(max_length = 50, default=None, choices=Coursework_Type)
    module=models.CharField(max_length = 10, default="AI")

class HDL_Coursework(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="module_convenor2",default='1')
    Title = models.CharField(max_length=50,null=True,default=None,blank=True)
    Submission_Date= models.DateTimeField(null=True,default=None,blank=True)
    Type = models.CharField(max_length = 50, default=None, choices=Coursework_Type)
    module=models.CharField(max_length = 10, default="HDL")

class PE_Coursework(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="module_convenor3",default='1')
    Title = models.CharField(max_length=50,null=True,default=None,blank=True)
    Submission_Date= models.DateTimeField(null=True,default=None,blank=True)
    Type = models.CharField(max_length = 50, default=None, choices=Coursework_Type)
    module=models.CharField(max_length = 10, default="PE")


class AI_Document(models.Model):
    def get_upload_path(self, filename, title):
        return rename_uploaded_file(filename, title)

    Coursework = models.ForeignKey(AI_Coursework, on_delete=models.CASCADE,default='1', related_name="ai_coursework")
    
    submitted_by = models.CharField(max_length=50,null=True,default=None,blank=True)

    docfile_individual = models.FileField(max_length = 200,upload_to=rename_uploaded_file, null=True,default=None,blank=True)
    docfile_group = models.FileField(max_length = 200,upload_to=rename_uploaded_file,null=True,default=None,blank=True)

    submission_id=models.CharField(max_length = 50,null=True,default=None,blank=True)
    submission_timestamp = models.DateTimeField(null=True,default=None,blank=True)

    similarity = models.DecimalField(null=True,default=None, max_digits=4, decimal_places=2)
    grade = models.DecimalField(null=True,default=None, max_digits=4, decimal_places=2)

    leader_approval = models.CharField(max_length=50,  default='Not Required')
    lecturer_signature = models.BooleanField(default=False)

    signature_timestamp = models.DateTimeField(null=True,default=None,blank=True)
    signed_by = models.CharField(max_length=50,  default='None')

    access_id = models.CharField(max_length = 50,null=True,default=None,blank=True)
    


class HDL_Document(models.Model):
    Coursework = models.ForeignKey(HDL_Coursework, on_delete=models.CASCADE,default='1', related_name="hdl_coursework")
    docfile_individual = models.FileField(max_length = 200,upload_to=rename_uploaded_file, null=True,default=None,blank=True)
    docfile_group = models.FileField(max_length = 200,upload_to=rename_uploaded_file,null=True,default=None,blank=True)
    submitted_by = models.CharField(max_length=50,null=True,default=None,blank=True)
    submission_id=models.CharField(max_length = 50,null=True,default=None,blank=True)
    submission_timestamp = models.DateTimeField(null=True,default=None,blank=True)
    
    similarity = models.DecimalField(null=True,default=None, max_digits=4, decimal_places=2)
    grade = models.DecimalField(null=True,default=None, max_digits=4, decimal_places=2)

    leader_approval = models.CharField(max_length=50,  default='Not Required')
    lecturer_signature = models.BooleanField(default=False)

    signature_timestamp = models.DateTimeField(null=True,default=None,blank=True)
    signed_by = models.CharField(max_length=50,  default='None')

    access_id = models.CharField(max_length = 50,null=True,default=None,blank=True)
    

class PE_Document(models.Model):
    Coursework = models.ForeignKey(PE_Coursework, on_delete=models.CASCADE,default='1', related_name="pe_coursework")
    docfile_individual = models.FileField(max_length = 200,upload_to=rename_uploaded_file,null=True,default=None,blank=True)
    docfile_group = models.FileField(max_length = 200,upload_to=rename_uploaded_file,null=True,default=None,blank=True)
    submitted_by = models.CharField(max_length=50,null=True,default=None,blank=True)
    submission_id=models.CharField(max_length = 50,null=True,default=None,blank=True)
    submission_timestamp = models.DateTimeField(null=True,default=None,blank=True)
    similarity = models.DecimalField(null=True,default=None, max_digits=4, decimal_places=2)
    grade = models.DecimalField(null=True,default=None, max_digits=4, decimal_places=2)
    leader_approval = models.CharField(max_length=50, default='Not Required')
    lecturer_signature = models.BooleanField(default=False)

    signature_timestamp = models.DateTimeField(null=True,default=None,blank=True)
    signed_by = models.CharField(max_length=50,  default='None')

    access_id = models.CharField(max_length = 50,null=True,default=None,blank=True)

    
class Additional_User_Info(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="additional",default='1')
    role=models.CharField(max_length = 50, default=None, choices=Roles)
    module_convenor = models.CharField(max_length = 50, null=True,default=None,blank=True, choices=modules)
    
    number = PhoneNumberField(
        verbose_name="Phone",
        max_length=30,
        default='',
        blank=True)

    extension = models.CharField(
        verbose_name="Extension",
        max_length=30,
        default='',
        blank=True)
    
    default_authentication_method=models.CharField(max_length=10, choices=Auth_meth, default='FIDO')

    # edit model to allow choices
    # for form link to model the choices have to be created in model instead of form
    multi_factor_authentication_method=MultiSelectField(choices=Auth_meth,
                                 max_length=20, 
                                 min_choices = 2,
                                 null=True,default=None,blank=True)
    digital_signature = models.CharField(max_length=50, default='Not Required')
    digital_signature_timestamp = models.DateTimeField(null=True,default=None,blank=True)


    

    
class leader_approval_list(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="approval_list",default='1')
    module=models.CharField(max_length = 10, default=None, choices=modules)
    submission_title = models.CharField(max_length=50,null=True,default=None,blank=True)
    access_id = models.CharField(max_length = 50,null=True,default=None,blank=True)
    pending_approval = models.BooleanField(default=False)