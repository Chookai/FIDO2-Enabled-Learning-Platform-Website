from fido2.client import Fido2Client
from fido2.server import Fido2Server, PublicKeyCredentialRpEntity
from fido2.webauthn import AttestationObject, AuthenticatorData, CollectedClientData
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
# from django.template.context import RequestContext
import simplejson
from fido2 import cbor
from django.http import HttpResponse
from django.conf import settings
from .models import *

from fido2.utils import websafe_decode, websafe_encode

from fido2.webauthn import AttestedCredentialData
from webauthn.views import login, add_log
from home.models import Additional_User_Info
import datetime
from home.views import send_email
# from .Common import get_redirect_url
from django.utils import timezone
from django.http import JsonResponse
from home.models import AI_Document, HDL_Document, PE_Document, Additional_User_Info, AI_Coursework, PE_Coursework, HDL_Coursework, leader_approval_list

def getServer():
    """Get Server Info from settings and returns a Fido2Server"""
    rp = PublicKeyCredentialRpEntity(id=settings.FIDO_SERVER_ID, name=settings.FIDO_SERVER_NAME)
    return Fido2Server(rp)


def begin_registration(request):
    """Starts registering a new FIDO Device, called from API"""
    
    server = getServer()
    
    user=User.objects.get(username__iexact=request.session.get('username'))
   
    registration_data, state = server.register_begin({
        u'id': user.username.encode("utf8"),
        u'name': (user.first_name + " " + user.last_name),
        u'displayName': user.username,
    }, getUserCredentials(user.username))

    request.session['fido_state'] = state
    # state is the challenge 
 
    return HttpResponse(cbor.encode(registration_data), content_type = 'application/octet-stream')


@csrf_exempt
def complete_reg(request):
    """Completes the registration, called by API"""
    # state is the challenge
    try:
       
        data = cbor.decode(request.body)

        client_data = CollectedClientData(data['clientDataJSON'])
        # whats tpm (Trusted Platform Module used by Microsoft)
        att_obj = AttestationObject((data['attestationObject']))
        server = getServer()
        auth_data = server.register_complete(
            request.session.pop('fido_state'),
            client_data,
            att_obj
        )
        encoded = websafe_encode(auth_data.credential_data)
        uk = FIDO_Authenticator()
      
        uk.user=User.objects.get(username__iexact=request.session.get('username'))
        uk.username = request.session.get('username')
        uk.properties = {"device": encoded, "type": att_obj.fmt, }
        uk.owned_by_enterprise = getattr(settings, "FIDO_KEY_ISSUER",None)
        uk.key_type = "FIDO2"
        uk.save()
    
        return HttpResponse(simplejson.dumps({'status': 'OK'}))
        
    except Exception as exp:
        

        return JsonResponse({'status': 'ERR', "message": "Error on server, please try again later"})

# Begin registration 
def start(request):
    """Start Registration a new FIDO Token"""
    context = csrf(request)
    return render(request, "webauthn/Add.html", context)

def getUserCredentials(username):
    credentials = []
    for uk in FIDO_Authenticator.objects.filter(username = username, key_type = "FIDO2"):
        
        # This is the public key
       
        credentials.append(AttestedCredentialData(websafe_decode(uk.properties["device"])))
    return credentials


def auth(request):
    context = csrf(request)
    context["username"] = request.user.username
    return render(request, "webauthn/Auth.html", context)


# 1
# Get FIDO2 Server from here 
def authenticate_begin(request):

    server = getServer()

    credentials = getUserCredentials(request.session.get("username", request.user.username))
    auth_data, state = server.authenticate_begin(credentials)
    request.session['fido_state'] = state
    
    return HttpResponse(cbor.encode(auth_data), content_type = "application/octet-stream")


# 2
@csrf_exempt
def authenticate_complete(request):
    
    try:
        credentials = []
        username = request.session.get("username", request.user.username)
        
        # get the js api
        server = getServer()

        credentials = getUserCredentials(username)
        data = cbor.decode(request.body)
        credential_id = data['credentialId']
        client_data = CollectedClientData(data['clientDataJSON'])
        auth_data = AuthenticatorData(data['authenticatorData'])
        signature = data['signature']
        
        try:
            # stores the credentials in cred, not calling the function 
            cred = server.authenticate_complete(
                request.session.pop('fido_state'),
                credentials,
                credential_id,
                client_data,
                auth_data,
                signature
            )
        except ValueError:
            return HttpResponse(simplejson.dumps({'status': "ERR",
                                                  "message": "Wrong challenge received, make sure that this is your security and try again."}),
                                content_type = "application/json")
        except Exception as excep:
            
            return HttpResponse(simplejson.dumps({'status': "ERR",
                                                  "message": str(excep)}),
                                content_type = "application/json")

            
        keys = FIDO_Authenticator.objects.filter(username = username, key_type = "FIDO2")

        for k in keys:
            if AttestedCredentialData(websafe_decode(k.properties["device"])).credential_id == cred.credential_id:
                if request.session.get('Session') == 'Submission':
                    cw = request.session.get('Coursework')
                    
                    if request.session.get('Module') == 'AI':
                       
                        try:
                            doc = AI_Document.objects.get(
                                Coursework__Title=cw, submitted_by=request.user.username)
                            doc.submission_id = uuid.uuid1()
                            doc.submission_timestamp = timezone.now()
                            
                            doc.save()
                          
                        except AI_Document().DoesNotExist:

                            doc = AI_Document()

                    elif request.session.get('Module') == 'PE':
                      
                        try:
                            doc = PE_Document.objects.get(
                                Coursework__Title=cw, submitted_by=request.user.username)
                            doc.submission_id = uuid.uuid1()
                            doc.submission_timestamp = timezone.now()
                            
                            doc.save()
                            
                        except PE_Document().DoesNotExist:

                            doc = PE_Document()
                        
                    elif request.session.get('Module') == 'HDL':
                    
                        try:
                            doc = HDL_Document.objects.get(
                                Coursework__Title=cw, submitted_by=request.user.username)
                            doc.submission_id = uuid.uuid1()
                            doc.submission_timestamp = timezone.now()
                            doc.save()
                            
                        except HDL_Document().DoesNotExist:

                            doc = HDL_Document() 
                   
                    # send_email(request,doc.submission_id,cw)
                # elif request.session.get('Session') == 'Signature':



                userr = User.objects.get(username__iexact=request.session.get('username'))
                addtionalInfo = Additional_User_Info.objects.get(user=userr)

                if request.session.get('Multi_Factor_Authentication') == True:
                    if addtionalInfo.multi_factor_authentication_method[0] == "FIDO":
                        del addtionalInfo.multi_factor_authentication_method[0]
                        addtionalInfo.save()
                        
                      

                    if addtionalInfo.multi_factor_authentication_method != []:
                        return redirect("/"+addtionalInfo.multi_factor_authentication_method[0]+'/')
                    else:
                        request.session['Multi_Factor_Authentication'] = False
                        request.session['Mode'] = 'FIDO'
                        addtionalInfo.multi_factor_authentication_method = request.session['Multi_Factor_Authentication_data']
                        addtionalInfo.save()
                        log = add_log(request)
                        res = login(request)

                else:
                    request.session['Mode'] = 'FIDO'
                    
                    add_log(request)
                    res = login(request)
                    
    
                return HttpResponse(simplejson.dumps({'status': "OK", "redirect": res["location"]}),
                                    content_type = "application/json")
               

                    
    except Exception as exp:
        
        return HttpResponse(simplejson.dumps({'status': "ERR", "message": exp.message}),
                            content_type = "application/json")
    

