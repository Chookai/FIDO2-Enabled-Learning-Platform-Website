from django.contrib.auth.models import User

from .models import AI_Document,HDL_Document,PE_Document, Additional_User_Info, AI_Coursework, PE_Coursework, HDL_Coursework


def lecturer_section(request):
    user=User.objects.get(username__iexact=request.session.get('username'))
    context={}
    details={} 
    courseworks = {}
    try:
        userr = Additional_User_Info.objects.get(user=user)
        if userr.role == 'Lecturer':
            if request.session.get('Module') == "AI":
                # details = AI_Document.objects.all()

                courseworks = AI_Coursework.objects.all().prefetch_related('ai_coursework')
                
                individual_documents=AI_Document.objects.values('docfile_individual').exclude(docfile_individual='')
                group_documents=AI_Document.objects.values('docfile_group').exclude(docfile_group='')
                context={"individual_documents": individual_documents,
                    "group_documents": group_documents}
                
            elif request.session.get('Module') == "PE":
                # details = PE_Document.objects.all()
                
                courseworks = PE_Coursework.objects.all().prefetch_related('pe_coursework')

                individual_documents=PE_Document.objects.values('docfile_individual').exclude(docfile_individual='')
                group_documents=PE_Document.objects.values('docfile_group').exclude(docfile_group='')
                context={"individual_documents": individual_documents,
                    "group_documents": group_documents}
                
            elif request.session.get('Module') == "HDL":
                
                # details = HDL_Document.objects.all()

                courseworks = HDL_Coursework.objects.all().prefetch_related('hdl_coursework')

                individual_documents=HDL_Document.objects.values('docfile_individual').exclude(docfile_individual='')
                group_documents=HDL_Document.objects.values('docfile_group').exclude(docfile_group='')
                context={"individual_documents": individual_documents,
                        "group_documents": group_documents}       
        else:
                
                courseworks = {}
    except:
            context={}
            
            courseworks = {}
            
    return context,  courseworks
