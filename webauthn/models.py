from django.db import models
from jsonfield import JSONField
# from jose import jwt
from django.conf import settings
from django.contrib.auth.models import User

from phonenumber_field.modelfields import PhoneNumberField

from phonenumber_field.widgets import PhoneNumberPrefixWidget



import uuid

class FIDO_Authenticator(models.Model):
    
   
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="key")

    username=models.CharField(max_length = 50)
    

    properties=JSONField(null = True)
    added_on=models.DateTimeField(auto_now_add = True)
    key_type=models.CharField(max_length = 25,default = "FIDO")
    enabled=models.BooleanField(default=True)
    expires=models.DateTimeField(null=True,default=None,blank=True)

    last_used=models.DateTimeField(null=True,default=None,blank=True)
    
    owned_by_enterprise=models.CharField(max_length = 50,null=True,default=None,blank=True)

  
    def __unicode__(self):
        return "%s -- %s"%(self.username,self.key_type)

    def __str__(self):
        return self.__unicode__()

    class Meta:
        app_label='webauthn'

class activityLog(models.Model):

    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="log")
    username=models.CharField(max_length = 50, default=None)
    session=models.CharField(max_length = 50)
    submission_id=models.CharField(max_length = 50)
    type=models.CharField(max_length = 50)
    timestamp=models.DateTimeField(null=True,default=None,blank=True)

    def __str__(self):
        return self.__unicode__()
    

class OTP (models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="profile")
    mobile_number=models.CharField(max_length=15)
    otp=models.CharField(max_length=100,null=True,blank=True)
    # uid=models.CharField(default=f'{uuid.uuid4}',max_length=200)
    uid=models.UUIDField(
         primary_key = True,
         default = uuid.uuid4,
         editable = False)
