from django.shortcuts import render, redirect

from .forms import SignUpForm, LoginForm, Username_Form

from django.contrib.auth import login, authenticate
from django.contrib import messages

# new
from django.http import HttpResponseRedirect

from django.contrib.auth.models import User

from django.urls import reverse
from django.core.serializers.json import DjangoJSONEncoder
import json
import random

from webauthn.helpers import MessageHandler

from django.utils import timezone
from webauthn.models import OTP, activityLog
import uuid
from home.models import Additional_User_Info
from phonenumbers import parse
from twilio.base.exceptions import TwilioException
from home.forms import AddtionalInfoForm
# Create your views here.


def login_view(request):
    # LoginForm
    form = Username_Form(request.POST or None)
    # form = LoginForm(request.POST or None)
    context = {}
    msg = None
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")

            try:
                del request.session['Multi_Factor_Authentication']
            except KeyError:
                pass

            if User.objects.filter(username=username):
                user = User.objects.get(username__iexact=username)
                try:
                    addtionalInfo = Additional_User_Info.objects.get(user=user)
                    if addtionalInfo.multi_factor_authentication_method:
                        request.session['Multi_Factor_Authentication_data'] = addtionalInfo.multi_factor_authentication_method
                        request.session['Multi_Factor_Authentication'] = True
                    else:
                        request.session['Multi_Factor_Authentication'] = False


                except Additional_User_Info.DoesNotExist:
                    pass

                request.session["username"] = username
                request.session['Session'] = "Authentication"

                return redirect('/authentication_method/')

            else:
                msg = 'Invalid user... Please try again.'

        else:
            msg = 'Error validating the form'

    return render(request, "authentication/login.html", {"form": form, "msg": msg})


def authentication_method(request):
    user = User.objects.get(username__iexact=request.session.get('username'))
    addtionalInfo = Additional_User_Info.objects.get(user=user)
    auth_meth = None
    if request.session.get('Multi_Factor_Authentication') == True:

        return redirect("/"+addtionalInfo.multi_factor_authentication_method[0]+'/')
    else:
        request.session['Multi_Factor_Authentication'] == False
        auth_meth = addtionalInfo.default_authentication_method
       
        return redirect("/"+auth_meth+"/")


def choose_authentication_method(request):
    return render(request, "authentication/authentication_method.html")



def otp_authentication(request):
    otp = random.randint(1000, 9999)
    # Thats how they link to the one user key
    user = User.objects.get(username__iexact=request.session.get('username'))
    
    try:
        addtionalInfo = Additional_User_Info.objects.get(user=user)
        number = addtionalInfo.number
        
        OTP_Log = OTP.objects.create(
            user=user, mobile_number=number, otp=f'{otp}')
        mobile_number_str = str(number)
        response_data = json.dumps(mobile_number_str, cls=DjangoJSONEncoder)
        request.session['Mobile_Number'] = json.loads(response_data)
       
        try:

            messagehandler = MessageHandler(number, otp).send_otp_via_message()
        except TwilioException as e:
       
            messagehandler = MessageHandler(number, otp).send_otp_via_whatsapp()

        # send_otp_via_message()
      
        red = redirect(f'{OTP_Log.uid}/')
        
        red.set_cookie("can_otp_enter", True, max_age=600)
        return red
    except:
        msg = 'Phone Number Not Registered'
        return render(request, "authentication/authentication_method.html", {"msg": msg, "meth": False})

def otp_verify(request, uid):
    msg = None
    number = request.session.get('Mobile_Number')
    phone_number_display = '*'*(len(number)-len(number[-4:]))+number[-4:]
    
    if request.method == "POST":
        OTP_Log = OTP.objects.get(uid=uid)

        if request.COOKIES.get('can_otp_enter') != None:

            if(OTP_Log.otp == request.POST['otp']):
                userr = User.objects.get(
                    username__iexact=request.session.get('username'))
                addtionalInfo = Additional_User_Info.objects.get(user=userr)
                if request.session.get('Multi_Factor_Authentication') == True:
                    if addtionalInfo.multi_factor_authentication_method[0] == "OTP":
                        del addtionalInfo.multi_factor_authentication_method[0]
                        addtionalInfo.save()
                       
                    if addtionalInfo.multi_factor_authentication_method != []:
                        return redirect("/"+addtionalInfo.multi_factor_authentication_method[0]+'/')
                    else:
                        request.session['Multi_Factor_Authentication'] = False
                        request.session['Mode'] = 'OTP'
                        addtionalInfo.multi_factor_authentication_method = request.session[
                            'Multi_Factor_Authentication_data']
                        addtionalInfo.save()

                else:
                    request.session['Mode'] = 'OTP'
                    add_log(request)
                    return create_session(request, request.session.get('username'))
            else:
                msg = 'Wrong OTP.. Please Try Again'

            # return HttpResponse("10 minutes passed")
        else:
            msg = 'OTP expires... Please request a new one'
    return render(request, "webauthn/OTP_Auth.html", {'id': uid, "msg": msg, 'number':phone_number_display})

def password_authentication(request):

    form = LoginForm(request.POST or None)
   
    msg = None
    if request.method == "POST":

        if form.is_valid():

            username = request.session.get('username')
            password = form.cleaned_data.get("password")

            user = authenticate(username=username, password=password)

            if user:
                userr = User.objects.get(
                username__iexact=request.session.get('username'))
                addtionalInfo = Additional_User_Info.objects.get(user=userr)
                if request.session.get('Multi_Factor_Authentication') == True:
                    if addtionalInfo.multi_factor_authentication_method[0] == "Password":
                        del addtionalInfo.multi_factor_authentication_method[0]
                        addtionalInfo.save()
                        
                    if addtionalInfo.multi_factor_authentication_method == []:
                        request.session['Multi_Factor_Authentication'] = False
                        request.session['Mode'] = 'Password'
                        addtionalInfo.multi_factor_authentication_method = request.session[
                            'Multi_Factor_Authentication_data']
                        addtionalInfo.save()
                        add_log(request)
                        return create_session(request, request.session.get('username'))
                        
                    else:
                        return redirect("/"+addtionalInfo.multi_factor_authentication_method[0]+'/')
                        

                else:
                    request.session['Mode'] = 'Password'
                    add_log(request)
                    return create_session(request, request.session.get('username'))

            else:
                msg = 'Invalid credentials'

        else:
            msg = 'Error validating the form'

    return render(request, "authentication/login.html", {"form": form, "msg": msg, "mode": 'Password'})

def fido_authentication(request):
    from webauthn.helpers import has_mfa
    res = has_mfa(username=request.session.get("username"), request=request)
    if res:
        if res == "Not Found":
            msg = 'FIDO Key Not Registered'
       
            return render(request, "authentication/authentication_method.html", {"msg": msg, "meth": False})
        else:
            return res
        
def add_log(request):
    log = activityLog()

    log.user = User.objects.get(
        username__iexact=request.session.get('username'))

    log.username = request.session.get('username')
    if request.session.get('Session') == "Submission":
        log.submission_id = uuid.uuid1()

    else:
        log.submission_id = "None"

    log.type = request.session.get('Mode')

    log.session = request.session.get('Session')
    log.timestamp = timezone.now()
    
    log.save()
    return None

def create_session(request, username):
    user = User.objects.get(username=username)
    user.backend = 'django.contrib.auth.backends.ModelBackend'

    # login using username only
    login(request, user)

    return HttpResponseRedirect(reverse('home'))
    # If does not have mfa redirect to home page


def register_new_user(request):
    msg = None
    success = False
    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            request.session['Session'] = "Registration"
            
            form.save()
            username = form.cleaned_data.get("username")
            request.session['username'] = username
            return redirect('/register_additional_info/')

        else:
            if bool(form.errors.get('username')):
                
                for error in form.errors.get('username'):
                    msg = error

    else:
        form = SignUpForm()

    return render(request, "authentication/register.html", {"form": form, "msg": msg, "success": success})


def register_new_user_additionalInfo(request):
    user = User.objects.get(username__iexact=request.session.get('username'))
    form = AddtionalInfoForm(request.POST, user=user)
    context = {}
    msg = []
    if request.method == 'POST':
        
        if form.is_valid:
            try:
                form.save()
                multi_auth = form.cleaned_data.get(
                    "multi_factor_authentication_method")
                default_auth = form.cleaned_data.get(
                    "default_authentication_method")
                for a in multi_auth:
                    if a == "FIDO":
                        return redirect("/fido2/")
                if default_auth == "FIDO":
                    return redirect("/fido2/")

                success = True
                return redirect("/login/")
            except ValueError:

                if bool(form.errors.get('multi_factor_authentication_method')):

                    for a in form.errors.get('multi_factor_authentication_method'):
                        msg.append(a)

                if bool(form.errors.get('module')):
                    for a in form.errors.get('module'):
                        msg.append(a)
        else:

            form = AddtionalInfoForm()

    else:
        form = AddtionalInfoForm(request.POST, user=user)

    return render(request, "authentication/register_additional_info.html", {"form": form, "msg": msg})
