from django.shortcuts import render
from django.shortcuts import render

from .models import AI_Document, HDL_Document, PE_Document, AI_Coursework, PE_Coursework, HDL_Coursework, leader_approval_list
from home.views import send_email
from .forms import UploadForm_Individual, UploadForm_Group, AI_CourseworkForm, HDL_CourseworkForm, PE_CourseworkForm, LeaderForm, GradeForm, edit_Submission
from django.shortcuts import redirect, reverse

from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from webauthn.helpers import has_mfa
from .lecturer import lecturer_section
from django.conf import settings
import os
import sys
import datetime
from cryptography.hazmat import backends
from cryptography.hazmat.primitives.serialization import pkcs12
from django.core.files import File
from endesive.pdf import cms
from django.forms import formset_factory

def leader_review(request, access_id):
    list = leader_approval_list.objects.get(access_id=access_id)
    
    if list.module == "AI":
        context = {'leader_doc': AI_Document.objects.filter(
            access_id=access_id)}
        edit_Sub = AI_Document.objects.get(access_id=access_id)

    elif list.module == "PE":
        context = {'leader_doc': PE_Document.objects.filter(
            access_id=access_id)}
        edit_Sub = PE_Document.objects.get(access_id=access_id)

    elif list.module == "HDL":
        context = {'leader_doc': HDL_Document.objects.filter(
            access_id=access_id)}
        edit_Sub = HDL_Document.objects.get(access_id=access_id)

    request.session['Leader_Signature'] = True

    if request.method == 'POST':
        form = edit_Submission(request.POST, request.FILES)
        if form.is_valid():
            edit_Sub.docfile_group = request.FILES['docfile_group']
            edit_Sub.save()
            return digital_signature_start(request, access_id)
        else:
            id = request.POST.get('access_id')
            request.session['ID'] = id
            return redirect('digital_signature_start')
            

    else:
        form = edit_Submission()

    return render(request, 'Modules/Student/LeaderViewPage.html', {'form': form, 'context': context, 'title': list.submission_title})

def digital_signature_onPDF(request, path, role, box):

    date = datetime.datetime.now()
    date = date.strftime('%Y-%m-%d %H:%M:%S %Z%z')
    grade = request.session.get('Grade')
    print(grade)
    print(request.session.get('Leader_Signature'))
    if request.session.get('Leader_Signature') == True:
        signature = role + ' Signed by : ' + request.user.username + '\n' + date

    else:
        signature = role + ' Signed by : ' + request.user.username + '\n' + date + '\n'+ 'Grade : ' + str(grade)

    dct = {
        "aligned": 8192,
        "sigflags": 3,
        "sigflagsft": 132,
        "sigpage": 0,
        # "sigbutton": True,
        "sigfield": "Signature1",
        "auto_sigfield": True,
        # "sigandcertify": True,
        # (x,y,width, length)
        "signaturebox": (box, -100, 590, 155),
        "signature": signature ,
        # "signature_img": "signature_test.png",
        "contact": "efysc1@nottingham.edu.my",
        "location": "Semenyih",
        "signingdate": date,
        "reason": "Digital Signature",
        "password": "1234",
    }

    if role == "Leader":
        
        with open("SSL_Certificates/leader_certificate.p12", "rb") as fp:
            p12 = pkcs12.load_key_and_certificates(
                fp.read(), b"Django1234", backends.default_backend()
            )
        fname = path
        datau = open(fname, "rb").read()
        datas = cms.sign(datau, dct, p12[0], p12[1], p12[2], "sha256")
        fname = fname.replace(".pdf", "-signedByLeader.pdf")

        # os.path.join(settings.MEDIA_ROOT, docfile_path1.name)
        with open(fname, "wb") as fp:
            fp.write(datau)
            fp.write(datas)
        return fname

    elif role == "Lecturer":
        with open("SSL_Certificates/lecturer_certificate.p12", "rb") as fp:
            p12 = pkcs12.load_key_and_certificates(
                fp.read(), b"Django1234", backends.default_backend()
            )
        fname = path
        datau = open(fname, "rb").read()
        datas = cms.sign(datau, dct, p12[0], p12[1], p12[2], "sha256")
        fname = fname.replace(".pdf", "-signedByLecturer.pdf")
        with open(fname, "wb") as fp:
            fp.write(datau)
            fp.write(datas)

        return fname

def one_off_digital_signature_start(request, cw_title):
   
    request.session['Session'] = "One_Off_Signature"
    request.session['cw_Title'] = cw_title

    res = has_mfa(username=request.user.username, request=request)

    if res == "Not Found":
        request.session["FIDO_Key"] = "Not Available"
        return redirect(request.session.get('Module'))
    else:
        request.session["FIDO_Key"] = "Available"
        return res

def one_off_digital_signature_complete(request):

    if request.session.get('Module') == 'AI':
        Title = request.session.get('cw_Title')
        cw = AI_Document.objects.filter(Coursework__Title=Title)
    
    elif request.session.get('Module') == 'HDL':
       
        cw = HDL_Document.objects.filter(Coursework__Title=request.session.get('cw_Title'))
    elif request.session.get('Module') == 'PE':
       
        cw = PE_Document.objects.filter(Coursework__Title=request.session.get('cw_Title'))
        
    for a in cw:
        
        role= "Lecturer"
        box = 300
        if  a.Coursework.Type == "Individual":
            docfile_path1 = a.docfile_individual.path
            dir_path = os.path.dirname(a.docfile_individual.name)
            
            targetPath = dir_path.split("/")[0:3]
            
            targetPath = "/".join(targetPath)
           
            docfile_path = digital_signature_onPDF(
                request, docfile_path1, role, box)

        elif a.Coursework.Type == "Group":
            docfile_path1 = a.docfile_group.path
            dir_path = os.path.dirname(a.docfile_group.name)
          
            targetPath = dir_path.split("/")[0:3]
           
            targetPath = "/".join(targetPath)
           
            docfile_path = digital_signature_onPDF(
                request, docfile_path1, role, box)
            
        
        with open(docfile_path, 'rb') as f:
            new_file = File(f)
        
        if  a.Coursework.Type == "Individual":
            a.docfile_individual.name = targetPath + \
            "/" + os.path.basename(docfile_path)
            print(a.docfile_individual.name)
            a.docfile_individual.file = new_file
        elif a.Coursework.Type == "Group":
            a.docfile_group.name = targetPath + \
            "/" + os.path.basename(docfile_path)
            a.docfile_group.file = new_file
        a.lecturer_signature = 1
        a.grade = 90
        request.session['Grade'] = a.grade
        a.signature_timestamp = timezone.now()
        a.signed_by = request.user.username
        a.save()

    return redirect(reverse(request.session.get('Module')))


def digital_signature_start(request):
    
    # print(cw.lecturer_signature)
    
    request.session['Session'] = "Signature"
    
    res = has_mfa(username=request.user.username, request=request)

    if res == "Not Found":
        request.session["FIDO_Key"] = "Not Available"
        return redirect(request.session.get('Module'))
    else:
        request.session["FIDO_Key"] = "Available"
        return res

def digital_signature_complete(request):

    if request.session.get('Leader_Signature') == True:
        list = leader_approval_list.objects.get(
            access_id=request.session.get('ID'))
        list.pending_approval = False
        list.save()
        request.session['Module'] = list.module
        if list.module == "AI":
            doc = AI_Document.objects.get(
                access_id=request.session.get('ID'))

        elif list.module == "PE":
            doc = PE_Document.objects.get(
                access_id=request.session.get('ID'))

        elif list.module == "HDL":
            doc = HDL_Document.objects.get(
                access_id=request.session.get('ID'))

        doc.leader_approval = 'Done'
        role = "Leader"
        box = 30

        docfile_path1 = doc.docfile_group.path

        dir_path = os.path.dirname(doc.docfile_group.name)
        
        targetPath = dir_path.split("/")[0:3]
        
        targetPath = "/".join(targetPath)

        docfile_path = digital_signature_onPDF(
            request, docfile_path1, role, box)

        with open(docfile_path, 'rb') as f:
            new_file = File(f)

        if doc.Coursework.Type == 'Individual':
            doc.docfile_individual.name = targetPath + \
                os.path.basename(docfile_path)
            doc.docfile_individual.file = new_file
        elif doc.Coursework.Type == 'Group':
            doc.docfile_group = targetPath + "/" + \
                os.path.basename(docfile_path)
            doc.docfile_group.file = new_file

        doc.save()
        request.session['Leader_Signature'] = False
        return redirect(reverse(request.session.get('Module')))

    else:

        if request.session.get('Module') == 'AI':
            
            cw = AI_Document.objects.get(
                submission_id=request.session.get('ID'))

        elif request.session.get('Module') == 'PE':
            
            cw = PE_Document.objects.get(
                submission_id=request.session.get('ID'))
        elif request.session.get('Module') == 'HDL':
            cw = HDL_Document.objects.get(
                submission_id=request.session.get('ID'))
        role = "Lecturer"
        box = 300

        if cw.Coursework.Type == 'Individual':
            docfile_path1 = cw.docfile_individual.path

            dir_path = os.path.dirname(cw.docfile_individual.name)
           
            targetPath = dir_path.split("/")[0:3]
            
            targetPath = "/".join(targetPath)
            
            docfile_path = digital_signature_onPDF(
                request, docfile_path1, role, box)

        elif cw.Coursework.Type == 'Group':
            docfile_path1 = cw.docfile_group.path

            dir_path = os.path.dirname(cw.docfile_group.name)
         
           
            targetPath = dir_path.split("/")[0:3]
           
            targetPath = "/".join(targetPath)
       
            docfile_path = digital_signature_onPDF(
                request, docfile_path1, role, box)

        with open(docfile_path, 'rb') as f:
            new_file = File(f)

        if cw.Coursework.Type == 'Individual':
            cw.docfile_individual.name = targetPath + \
                "/" + os.path.basename(docfile_path)
            cw.docfile_individual.file = new_file
        elif cw.Coursework.Type == 'Group':
            cw.docfile_group.name = targetPath + \
                "/" + os.path.basename(docfile_path)
            cw.docfile_group.file = new_file

        cw.grade = request.session.get('Grade')
        cw.lecturer_signature = 1
        cw.signature_timestamp = timezone.now()
        cw.signed_by = request.user.username
        cw.save()

        return redirect(reverse(request.session.get('Module')))


def Submission_Page(request, Title):
    request.session['Session'] = "Submission"
    msg = {}
    context = {}
    if request.session.get('Module') == 'AI':
        cw = AI_Coursework.objects.get(Title=Title)
        try:
            doc = AI_Document.objects.get(
                Coursework=cw, submitted_by=request.user.username)
            context = {'list': doc}
        except AI_Document().DoesNotExist:

            doc = AI_Document()

    elif request.session.get('Module') == 'PE':
        cw = PE_Coursework.objects.get(Title=Title)
        try:
            doc = PE_Document.objects.get(
                Coursework=cw, submitted_by=request.user.username)
            context = {'list': doc}
        except PE_Document().DoesNotExist:

            doc = PE_Document()
        
    elif request.session.get('Module') == 'HDL':
        cw = HDL_Coursework.objects.get(Title=Title)
        try:
            doc = HDL_Document.objects.get(
                Coursework=cw, submitted_by=request.user.username)
            context = {'list': doc}
        except HDL_Document().DoesNotExist:

            doc = HDL_Document()

    request.session['Type'] = cw.Type
    request.session['CW'] = Title

    if request.method == 'POST':
        form1 = UploadForm_Individual(request.POST, request.FILES)
        form2 = UploadForm_Group(request.POST, request.FILES)
        form3 = LeaderForm(request.POST)

        if form1.is_valid():
            doc.docfile_individual = request.FILES['docfile_individual']
            doc.Coursework = cw
            doc.submitted_by = request.session.get('username')
            doc.grade = 0
            doc.similarity = 10
            doc.lecturer_signature = False
            doc.save()

            request.session['Coursework'] = cw.Title

          
            res = has_mfa(username=request.user.username, request=request)
            if res:
                return res

        if form2.is_valid():

            doc.docfile_group = request.FILES['docfile_group']
            doc.Coursework = cw
            doc.submitted_by = request.session.get('username')
            doc.lecturer_signature = False
        
            request.session['Coursework'] = cw.Title

            if request.session.get('leader_username') == request.user.username:
                doc.leader_approval = 'Not Required'
            else:

                doc.leader_approval = 'Required'
                request.session['Leader_Approval'] = True
                doc.access_id = uuid.uuid4()
                leader = User.objects.get(
                    username=request.session.get('leader_username'))
                list = leader_approval_list()
                list.user = leader
                list.module = request.session.get('Module')
                list.submission_title = Title
                list.access_id = doc.access_id
                list.pending_approval = True
                list.save()

            doc.grade = 0
            doc.similarity = 10
            doc.save()

            
            
            res = has_mfa(username=request.user.username, request=request)
            if res:
                return res
            
        if form3.is_valid():

            leader_username = form3.cleaned_data.get("leader_username")

            if User.objects.filter(username=leader_username):
                msg = 'Valid'
                request.session['leader_username'] = leader_username
            elif leader_username == '':
                msg = 'Valid'
                request.session['leader_username'] = request.user.username
            else:
                msg = 'Invalid'
                
    else:
        form1 = UploadForm_Individual()  # A empty, unbound form
        form2 = UploadForm_Group()
        form3 = LeaderForm()

    context = {'form1': form1, 'form2': form2, 'form3': form3,
               'username': request.user.username, 'msg': msg, 'submission_list': context}

    return render(request, 'Modules/Student/submissionPage.html', context)


def AI_Page(request):
    # Handle file upload
    message = request.GET.get('message', None)
    request.session['Module'] = "AI"

    user = User.objects.get(username__iexact=request.session.get('username'))

    if request.method == 'POST':

        form = AI_CourseworkForm(request.POST, user=user)
        form2 = GradeForm(request.POST)
        if form.is_valid():
            request.session['Session'] = "Add Coursework"
            res = has_mfa(username=request.user.username, request=request)

            if res == "Not Found":
                request.session["FIDO_Key"] = "Not Available"
                return redirect(request.session.get('Module'))
            else:
                request.session["FIDO_Key"] = "Available"
                form.save()
                return res
        else:
            form = AI_CourseworkForm(request.POST, user=user)
        
        if form2.is_valid():
            id = request.POST.get('submission_id')
           
            grade = form2.cleaned_data['grade']
            
            request.session['Grade'] = grade
            request.session['ID'] = id
            request.session['Grade'] = grade
            return redirect('digital_signature_start')

    else:

        form = AI_CourseworkForm(request.POST, user=user)
        form2 = GradeForm()

    [doc, courseworks] = lecturer_section(request)
    cw = AI_Coursework.objects.all()

    context = {'form': form,'form2':form2, 'username': request.user.username,
               'doc': doc, 'details': courseworks, 'cw': cw}

    # Render list page with the documents and the form
    return render(request, 'Modules/Student/AI.html', context, message)


def HDL_Page(request):

    request.session['Module'] = "HDL"

    user = User.objects.get(username__iexact=request.session.get('username'))
    if request.method == 'POST':

        form = HDL_CourseworkForm(request.POST, user=user)
        form2 = GradeForm(request.POST)
        if form.is_valid():
            request.session['Session'] = "Add Coursework"
            res = has_mfa(username=request.user.username, request=request)
            

            if res == "Not Found":
                request.session["FIDO_Key"] = "Not Available"
                return redirect(request.session.get('Module'))
            else:
                request.session["FIDO_Key"] = "Available"
                form.save()
                return res
        if form2.is_valid():
            id = request.POST.get('submission_id')
           
            grade = form2.cleaned_data['grade']
            
            request.session['Grade'] = grade
            request.session['ID'] = id
            request.session['Grade'] = grade
            return redirect('digital_signature_start')
    else:

        form = HDL_CourseworkForm(request.POST, user=user)

        [doc, courseworks] = lecturer_section(request)
        cw = HDL_Coursework.objects.all()

        context = {'form': form, 'username': request.user.username,
                   'doc': doc, 'details': courseworks, 'cw': cw}
        return render(request, 'Modules/Student/HDL.html', context)




def PE_Page(request):

    request.session['Module'] = "PE"
    request.session['document_set'] = "pe_document_set"
    
    user = User.objects.get(username__iexact=request.session.get('username'))
   
   
    if request.method == 'POST':
        
        
        form = PE_CourseworkForm(request.POST, user=user)
        form2 = GradeForm(request.POST)
        
        if form.is_valid():
            request.session['Session'] = "Add Coursework"
            res = has_mfa(username=request.user.username, request=request)

            if res == "Not Found":
                request.session["FIDO_Key"] = "Not Available"
                return redirect(request.session.get('Module'))
            else:
                request.session["FIDO_Key"] = "Available"
                form.save()
                return res
        
        if form2.is_valid():
            id = request.POST.get('submission_id')
           
         
            # grade_value = request.POST.get('grade')
          
            grade = form2.cleaned_data['grade']
            print(grade)
            # for i in range(int(grade)):
            #     print(i)
            request.session['Grade'] = grade
            request.session['ID'] = id
            request.session['Grade'] = grade
            return redirect('digital_signature_start')
          
            

    else:
        
        form2 = GradeForm()
        form = PE_CourseworkForm(request.POST, user=user)
       
        [doc, courseworks] = lecturer_section(request)
        cw = PE_Coursework.objects.all()
        
        context = {'form': form, 'form2':form2,'username': request.user.username,
                   'doc': doc, 'details': courseworks, 'cw': cw}
        return render(request, 'Modules/Student/PE.html', context)
