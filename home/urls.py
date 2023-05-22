# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from home import views,modules
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name="home"),
   
  
    path('Submission_Page/<str:Title>/',modules.Submission_Page, name='Submission_Page'),
    path('leader_view_page/<str:access_id>',modules.leader_review,name = "Leader_view"),
    path('digital_signature_start/',modules.digital_signature_start,name='digital_signature_start'),
    path('digital_signature_complete/',modules.digital_signature_complete,name='digital_signature_complete'),
    path('one_off_digital_signature_start/<str:cw_title>',modules.one_off_digital_signature_start,name='one_off_digital_signature_start'),
     path('one_off_digital_signature_complete/',modules.one_off_digital_signature_complete,name='one_off_digital_signature_complete'),

    path('edit_profile/', views.edit_Profile, name="edit_profile"),
    
    path('',views.send_email, name='send_email'),

    
    path('registered/',views.registered,name='registered'),
    path('AI/',modules.AI_Page,name='AI'),
    path('HDL/', modules.HDL_Page, name = 'HDL'),
    path('Power_Electronics/', modules.PE_Page, name = 'PE'),


    
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


