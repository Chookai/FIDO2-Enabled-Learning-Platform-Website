from django.http import HttpResponse

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.urls import reverse
from django.shortcuts import render, get_object_or_404


from .models import AI_Coursework, HDL_Coursework, PE_Coursework

import datetime
from .forms import update_AddtionalInfoForm
from django.shortcuts import redirect
from django.contrib.auth.models import User

from .models import Additional_User_Info
from django.conf import settings

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import os

from django.core.serializers.json import DjangoJSONEncoder
import json

from cryptography.hazmat import backends
from cryptography.hazmat.primitives.serialization import pkcs12

from endesive.pdf import cms
from django.utils import timezone

# REDIRECT TO AUTH/LOGIN
@login_required()
def home(request):
    
    
    request.session["FIDO_Key"]=None
 
    user=User.objects.get(username__iexact=request.session.get('username'))
    context = {'CW' : AI_Coursework.objects.all()}
    context2 = {'CW' : PE_Coursework.objects.all()}
    context3 = {'CW' :HDL_Coursework.objects.all()}
   
    try:
        additionalInfo=Additional_User_Info.objects.get(user=user)
        request.session['role'] = additionalInfo.role
        request.session['Module_Convenor'] = additionalInfo.module_convenor

        mobile_number=additionalInfo.number  
        
        # WHY DO I USE SESSION TO STORE PROFILE INFORMATION 
        request.session['role'] = additionalInfo.role
        request.session['default_authentication_method'] = additionalInfo.default_authentication_method
        request.session['Action_Required'] = additionalInfo.digital_signature
        mobile_number_str = str(mobile_number)
        response_data = json.dumps(mobile_number_str, cls=DjangoJSONEncoder)
        request.session['Mobile'] = json.loads(response_data)
        
        request.session['Module'] = additionalInfo.module_convenor
        request.session['Module_Convenor'] = additionalInfo.module_convenor
    except:
        request.session['role'] = None
        request.session['default_authentication_method'] = None
        request.session['Mobile']="+6012345678"
        request.session['Module_Convenor'] = None
    

    return render(request,"home/home.html",{'AI_CW':context,'PE_CW':context2,'HDL_CW':context3,})

@login_required()
def registered(request):
    return render(request,"home/home.html",{"registered":True})


def send_email(request,submission_id,title):
    
    
    # ADD COURSEWORK TITLE and submission ID
    if request.session.get('Leader_Approval') == True :
        leader_user = User.objects.get(username =request.session.get('leader_username') ) 
        subject = 'Group_Coursework: '+ title + ' Leader Approval Required'
        
        html_message = render_to_string('email/Submission_email_leader.html', {'title':title,'username': request.user.username, 'submission_id':submission_id})
        plain_message = strip_tags(html_message)
        email_from = settings.EMAIL_HOST_USER
        to = leader_user.email

        send_mail(subject, plain_message, email_from, [to], html_message=html_message)

    else:

        subject = 'Coursework Submitted Receipt'
        
        html_message = render_to_string('email/Submission_email_student.html', {'title':title,'username': request.user.username,'submission_id':submission_id })
        plain_message = strip_tags(html_message)
        email_from = settings.EMAIL_HOST_USER
        to = request.user.email

        send_mail(subject, plain_message, email_from, [to], html_message=html_message)
    

   

def edit_Profile(request):
    form = None
    context ={}
    msg=None
    # NEED TO REFRESHS SESSION OBJECT WHEN ADDED 
    user=User.objects.get(username__iexact=request.session.get('username'))
    
    my_model = get_object_or_404(Additional_User_Info, user=user)
    
    if request.method == 'POST':
        form = update_AddtionalInfoForm(request.POST, instance=my_model)
        if form.is_valid():
            
            form.save()
            infoo = Additional_User_Info.objects.get(user=user)
            if infoo.role == "Lecturer":
                if bool(infoo.multi_factor_authentication_method) :
                    return redirect('/profile/')
                    
                else:
                    msg = 'Lecturer must enable multi factor authentication method!'
            else:
                return redirect('/profile/')

        else:
            msg = 'Must select up to two methods!'
    else:
        form = update_AddtionalInfoForm(instance=my_model)

    
    return render(request,"home/edit_profile.html",{"form": form, "msg": msg, "model":my_model})



