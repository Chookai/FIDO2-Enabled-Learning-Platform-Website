from django.shortcuts import render
from django.http import HttpResponse


from django.shortcuts import render
from django.http import HttpResponse
from .models import *

from django.conf import settings

from django.contrib.auth.decorators import login_required

from home.lecturer import lecturer_section
from home.models import Additional_User_Info, leader_approval_list

# Create your views here.

@login_required
def profile_Page(request):
    keys=[]
    
    context={"keys":FIDO_Authenticator.objects.filter(username=request.user.username)}
    context2={"logs":activityLog.objects.filter(username=request.user.username)}
    user=User.objects.get(username__iexact=request.session.get('username'))
    context4 = {"profile":Additional_User_Info.objects.filter(user=user)}
  
    context3={"leader_action":leader_approval_list.objects.filter(user=user)}
    
    print(context3)
    [doc,courseworks] = lecturer_section(request)

    for k in context["keys"]:
        
        k.name = getattr(settings,'MFA_RENAME_METHODS',{}).get(k.key_type,k.key_type)
       
        if k.key_type == "FIDO2":
            setattr(k,"device",k.properties.get("type","----"))
       
        keys.append(k)

    context["keys"]=keys
   
    
    return render(request,"home/profile.html",{"context1": context, "context2": context2,"context3": context3,"context4": context4,  "details": courseworks})

@login_required
def deleteKey(request):

    key=FIDO_Authenticator.objects.get(id=request.GET.get('id'))
    if key.username == request.user.username:
        key.delete()
        
        return HttpResponse('Deleted Successfully')
    else:
        return HttpResponse("Error")
    

def login(request):
    from django.conf import settings
    func_call = retrieve_callable_function(settings.CREATE_SESSION_CALL)
    
    print(func_call(request,username=request.session["username"]))
    
    # it creates a callable function. For instance, it calls create_sesion that takes username as a variable
    # and get the return value from create session and return it to login and return to res in FIDO2.py
    # this prevents circular import where views are dependant to each other
    # it happens when two or more modules depend on each other
    return func_call(request,username=request.session["username"])

def add_log(request):
    from django.conf import settings
    func_call = retrieve_callable_function(settings.ADD_LOG_CALL)
    return func_call(request)

def retrieve_callable_function(function_path):
    import importlib
    parsed_str = function_path.split(".")
    module_name , function_name = ".".join(parsed_str[:-1]) , parsed_str[-1]
    imported_module = importlib.import_module(module_name)
    callable_func = getattr(imported_module,function_name)


    if not callable_func:
        raise Exception("Module does not have requested function")
    return callable_func


