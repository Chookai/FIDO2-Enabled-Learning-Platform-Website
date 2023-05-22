# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from webauthn import views
from . import FIDO2
try:
    from django.urls import  re_path as url
except:
     from django.conf.urls import  url

# views file could be place anywhere as long as you import the views 


urlpatterns = [
  
    path('Delete_Key/',views.deleteKey, name='delete_Key'),
    path('profile/',views.profile_Page, name="profile_page"),
 
    

    url(r'fido2/auth/', FIDO2.auth, name="fido2_auth"),
    url(r'fido2/begin_auth/', FIDO2.authenticate_begin, name="fido2_begin_auth"),
    url(r'fido2/complete_auth/', FIDO2.authenticate_complete, name="fido2_complete_auth"),
    url(r'fido2/begin_reg/', FIDO2.begin_registration, name="fido2_begin_reg"),
    url(r'fido2/complete_reg/', FIDO2.complete_reg, name="fido2_complete_reg"),
    url(r'fido2/$', FIDO2.start, name="start_fido2")

   
  
    
    
]
