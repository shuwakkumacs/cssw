import os
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Q
from django.core import serializers
from django.views.decorators.cache import never_cache
from django.contrib.admin.sites import site, AdminSite
from django.core.mail import EmailMessage
from .models import *
from .forms import *
import json
import hashlib
import copy
from .settings import settings
from datetime import datetime
import sys
import requests
import base64

# Create your views here.

@csrf_exempt
def test(request):
    #msg = EmailMessage('CSSW registration password reset','下記のURLからパスワードの変更を行ってください。※心当たりが無い場合は破棄してください。\nPlease proceed to the following URL to change your password. *Please ignore if you are not aware of this message.\nhttps://cssw.r9n.net\n\n--CSSW committee','csswreg@gmail.com',['ss.shwk@gmail.com','susumu@pcl.cs.waseda.ac.jp'])
    #msg.send()
    return HttpResponse("")

@csrf_exempt
def main(request):
    #access_token = request.COOKIES.get('access_token')
    #data_access_token = AccessToken.authorize(access_token)
    #if not data_access_token:
    #    response = redirect("../login/?mode=reg")
    #    response.delete_cookie("access_token")
    #    return response

    #form = ParticipantForm()
    #
    #return render(request, "program/main.html", context = {"form": form})
    return HttpResponse("")

@csrf_exempt
def registration_view(request):
    mode = request.GET.get(key="mode", default=None)
    err = request.GET.get(key="err", default=None)

    access_token = request.COOKIES.get('access_token')
    data_access_token = AccessToken.authorize(access_token)
    if mode=="edit":
        if not data_access_token:
            response = redirect("../login/?mode=reg")
            response.delete_cookie("access_token")
            return response

        participant = Participant.get_by_id(id=data_access_token.participant_id)
        programs = Program.get_by_participant_id(participant_id=participant.id)
        participant_form = ParticipantForm(instance=participant)
        participant_form.fields["password"].widget = HiddenInput()
        program_forms = []
        for program in programs:
            program_forms.append(ProgramForm(instance=program))
    else:
        if data_access_token:
            response = redirect("../registration/?mode=edit")
            return response

        participant_form = ParticipantForm()
        program_forms = []

    if settings["EXPIRATION"]["registration"] and (settings["EXPIRATION"]["registration_date"]-datetime.now()).total_seconds()<0:
        participant_form.fields["is_presenter"].widget.attrs["readonly"] = "readonly"
        if mode!="edit":
            participant_form.initial["is_presenter"] = "No"
            
    
    context = {
        "mode": mode,
        "settings": settings,
        "participant_form": participant_form,
        "program_forms": program_forms,
        "program_form_empty": ProgramForm()
    }
    return render(request, "program/registration.html", context=context)

@csrf_exempt
def registration(request):
    request_data = dict(request.POST)
    print(request_data)
    participant_keys = ["laboratory", "grade", "affiliation", "reference", "surname", "givenname", "surname_en", "givenname_en", "email", "password", "party_attendance", "is_presenter", "food_restriction", "comment"]
    program_keys = ["program_id", "title", "session_category", "require_table", "co_presenters"]

    redirect_url = "../../registration_complete/"

    postdata = { "participant": {}, "program": [] }
    for key in participant_keys:
        postdata["participant"][key] = request_data[key][0]

    if "title" in request_data:
        program_cnt = len(request_data["title"])
    else:
        program_cnt = 0
    for i in range(program_cnt):
        postdata["program"].append({})
        for key in program_keys:
            if key in request_data:
                postdata["program"][i][key] = request_data[key][i]
    
    pid = request_data["participant"][0]
    if pid != "":  # edit mode
        try:
            with transaction.atomic():
                participant = Participant.get_by_id(pid)
                postdata["participant"]["time_modified"] = timezone.now()
                f_pa = ParticipantForm(postdata["participant"], instance=participant)
                if f_pa.is_valid():
                    f_pa.save()
                    if postdata["participant"]["is_presenter"]=="Yes":
                        for data in postdata["program"]:
                            if data["program_id"] != -1:
                                data["participant"] = pid
                                program = Program.get_by_id(data["program_id"])
                                data["time_modified"] = timezone.now()
                                f_pr = ProgramForm(data, instance=program)
                            else:
                                del data["program_id"]
                                program = None
                                f_pr = ProgramForm(data)

                            if f_pr.is_valid():
                                f_pr.save()
                            else:
                                raise ValueError()
                else:
                    raise ValueError()
        except ValueError as e:
            redirect_url += "?err=invalid"

    else:  # register mode
        participant = Participant.objects.filter(Q(email=postdata["participant"]["email"]) | Q(surname=postdata["participant"]["surname"], givenname=postdata["participant"]["givenname"], laboratory=postdata["participant"]["laboratory"], grade=postdata["participant"]["grade"])).first()
        if participant:
            redirect_url += "?err=duplicate"
        else:
            try:
                with transaction.atomic():
                    postdata["participant"]["password"] = md5(request_data["password"][0])
                    f_pa = ParticipantForm(postdata["participant"])
                    if f_pa.is_valid():
                        new_participant = f_pa.save()
                        headers = {"Authorization": "Bearer qvWwSsgqH05qtR9jPUtbyGNBenpVomaFRASuSmjaSQA"}
                        payload = {"message": "{}{} {}{}".format(postdata["participant"]["surname"],postdata["participant"]["givenname"],postdata["participant"]["laboratory"],postdata["participant"]["grade"])}
                        requests.post("https://notify-api.line.me/api/notify", params=payload, headers=headers)
                        if postdata["participant"]["is_presenter"]=="Yes":
                            for data in postdata["program"]:
                                data["participant"] = new_participant.id
                                f_pr = ProgramForm(data)
                                if f_pr.is_valid():
                                    new_program = f_pr.save()
                                else:
                                    raise ValueError()
                    else:
                        raise ValueError()
            except ValueError:
                redirect_url += "?err=invalid"

    return redirect(redirect_url)

@csrf_exempt
def registration_complete_view(request):
    err = request.GET.get(key="err", default=None)
    context = {
        "err": err,
        "settings": settings
    }
    return render(request, "program/registration_complete.html", context=context)

@csrf_exempt
def signup_view(request):
    access_token = request.COOKIES.get('access_token')
    return redirect('../')

@csrf_exempt
def signup(request):
    request_data = json.loads(request.body)    
    access_token = generate_access_token()
    request_data["access_token"] = access_token
    try:
        participant = Participant.add(request_data)
        response = JsonResponse({"status": "success"})
        response.set_cookie("access_token", access_token, max_age=60*60*24)
        return response
    except Exception as e:
        return JsonResponse({"status": "failure", "error": e})

@csrf_exempt
def login_view(request):
    mode = request.GET.get(key="mode", default=None)
    err = request.GET.get(key="err", default=None)

    access_token = request.COOKIES.get('access_token')
    data_access_token = AccessToken.authorize(access_token)
    if data_access_token:
        if mode=="reg":
            response = redirect("../registration/?mode=edit")
        elif mode=="onsite":
            response = redirect("../../")
        response.delete_cookie("access_token")
        return response

    context = {
        "mode": mode,
        "settings": settings
    }
    if err=="invalid":
        context["errmsg"] = "許可されていないリクエストです。 Forbidden request."
    elif err=="unauthorized":
        context["errmsg"] = "Eメールかパスワードが間違っています。 Incorrect email/password."
        
    return render(request, "program/login.html", context=context)

# Give an existing access token to the new device
@csrf_exempt
def login(request):
    mode = request.GET.get(key="mode", default=None)
    request_data = dict(request.POST)
    for name,value in request_data.items():
        request_data[name] = value[0]
    participant = Participant.get(email=request_data["email"], password=request_data["password"])

    if participant:
        access_token = AccessToken.register(**request_data)

        edit_active = (settings["EXPIRATION"]["edit"] and settings["EXPIRATION"]["edit_date"]>datetime.now())
        onsite_active = (settings["EXPIRATION"]["onsite"] and settings["EXPIRATION"]["onsite_date"]>datetime.now())

        if (not mode) and (not edit_active==onsite_active):
            return redirect("../../login/?err=invalid")

        if mode=="reg":
            response = redirect("../../registration/?mode=edit")
        elif mode=="onsite":
            return redirect("../../")

        else: 
            if edit_active:
                return redirect("../../registration/?mode=edit")
            else:
                return redirect("../../")

        response.set_cookie("access_token", access_token, max_age=60*60*24)
        return response

    else:
        return redirect("../../login/?mode={}&err=unauthorized".format(mode))

@csrf_exempt
def password_forget_view(request):
    err = request.GET.get(key="err", default=None)
    context = {
        "settings": settings
    }
    if err=="na":
        context["errmsg"] = "メールアドレスが登録されていません。 Email address is not registered."
        
    return render(request, "program/password_forget.html", context=context)

@csrf_exempt
def send_email__password_reset(request):
    request_data = dict(request.POST)
    email = request_data["email"][0]
    participant = Participant.get_by_email(email=email)
    if participant:
        reset_token = PasswordResetSession.add(participant=participant)
        try:
            msg = EmailMessage('CSSW registration password reset','下記のURLからパスワードの変更を行ってください。※心当たりが無い場合は破棄してください。\nPlease proceed to the following URL to change your password. *Please ignore if you are not aware of this message.\nhttps://cssw.r9n.net/password_change/{}/\n\n--CSSW committee'.format(reset_token),'csswreg@gmail.com',[email])
            msg.send()
            return HttpResponse("メールアドレスにパスワード設定メールを送信しました。 Message for password reset has been sent to your email address.")
        except Exception as e:
            return HttpResponse(e)
    else:
        return redirect("/password_forget/?err=na")

@csrf_exempt
def password_change_view(request,reset_token):
    session = PasswordResetSession.get(reset_token=reset_token)
    if session:
        context = {
            "session_id": session.id,
            "settings": settings
        }
        return render(request, "program/password_change.html", context=context)
    else:
        return HttpResponse("Invalid access token.")

@csrf_exempt
def password_change(request):
    request_data = dict(request.POST)
    session_id = request_data["session_id"][0]
    password = request_data["password"][0]
    ret = PasswordResetSession.change_password(id=session_id,password=password)
    if ret:
        return HttpResponse("パスワードの変更を完了しました。 Your password has been changed.<br><br><a href='/login/?mode=reg'>ログイン Log in</a>")
    else:
        return HttpResponse("パスワードの変更にエラーが発生しました。 Error occurred while changing password.")

@never_cache
@csrf_exempt
def registration_list_view(request):
    #if not _basicAuth(request):
    #    return _http401()
    laboratory = request.GET.get(key="laboratory", default=None)
    programs = Program.get_with_participants(laboratory=laboratory)
    context = {
        "settings": settings,
        "programs": programs
    }
    return render(request, "program/registration_list.html", context=context)

@csrf_exempt
def get_registration_list(request):
    return JsonResponse(json.loads(serializers.serialize('json',program)), safe=False)

@csrf_exempt
def delete_program(request):
    request_data = dict(request.POST)
    program_id = request_data["id"][0]
    Program.delete_by_id(program_id)
    return HttpResponse("")


# Only for development
@csrf_exempt
def logout(request, redirect_fail=None):
    response = redirect('../../signup/')
    response.delete_cookie("access_token")
    return response

def check_session(access_token, redirect_to):
    if not AccessToken.authorize(access_token):
        response = redirect(redirect_to)
        response.delete_cookie("access_token")
        return response
    else:
        return None


