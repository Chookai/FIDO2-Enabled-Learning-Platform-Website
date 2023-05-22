
from .models import *
from . import FIDO2
import simplejson
from django.shortcuts import HttpResponse


from django.conf import settings
from twilio.rest import Client

from django.shortcuts import render

def has_mfa(request,username):
    message="Not Found"
    if FIDO_Authenticator.objects.filter(username=username,enabled=1).count()>0:
        context={
                    'mode':request.session.get('Session'),
                    'Module':request.session.get('Module')  
                } 
        
        return render(request,'webauthn/Auth.html', context)
        
    return message


class MessageHandler:
    phone_number=None
    otp=None
    def __init__(self,phone_number,otp) -> None:
        self.phone_number=phone_number
    
        self.otp=otp
    def send_otp_via_message(self):     
        client= Client(settings.ACCOUNT_SID,settings.AUTH_TOKEN)
        
        message=client.messages.create(body=f'your otp is:{self.otp}',from_=f'{settings.TWILIO_PHONE_NUMBER}',to=f'{settings.COUNTRY_CODE}{self.phone_number}')
                                    
    def send_otp_via_whatsapp(self):     
        client= Client(settings.ACCOUNT_SID,settings.AUTH_TOKEN)
        message=client.messages.create(body=f'your otp is:{self.otp}',from_=f'{settings.TWILIO_WHATSAPP_NUMBER}',to=f'whatsapp:{settings.COUNTRY_CODE}{self.phone_number}')
