import os
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import *
import json
import hashlib
import copy
from .settings import settings
from datetime import datetime
import sys

# Create your views here.

@csrf_exempt
def main(request):
    #access_token = request.COOKIES.get('access_token')
    #if not access_token:
    #    return redirect('signup/')
    #else:
    #    participant = authorize_by_access_token(access_token)
    #    if participant:
    #        program_history = ProgramHistory.get_all_for_participant(participant.id)
    #        context = {
    #            "program_history": program_history
    #        }
    #        return render(request, "program/main.html", context=context)
    return render(request, "program/main.html")

@csrf_exempt
def registration_view(request):
    labs = Laboratory.objects.all()
    grades = Grade.objects.all()
    context = {
        "labs": labs,
        "grades": grades,
        "session_categories": settings["SESSION_CATEGORIES"],
        "settings": settings
    }
    return render(request, "program/registration.html", context=context)

@csrf_exempt
def registration(request):
    request_data = dict(request.POST)
    participant_data = {
        "laboratory_id": request_data["laboratory_id"][0],
        "grade_id": request_data["grade_id"][0],
        "surname": request_data["surname"][0],
        "givenname": request_data["givenname"][0],
        "email": request_data["email"][0]
    }
    program_data = {
        "title": request_data["title"][0],
        "session_category": request_data["session_category"][0]
    }
    
    if "participant_id" in request_data:
        participant = Participant.get_by_id(request_data["participant_id"][0])
        program = Program.get_by_participant_id(request_data["participant_id"][0])

        participant.laboratory_id = participant_data["laboratory_id"] 
        participant.grade_id = participant_data["grade_id"] 
        participant.surname = participant_data["surname"] 
        participant.givenname = participant_data["givenname"] 
        participant.email = participant_data["email"] 
        participant.time_modified = timezone.now()
        participant.save()
        program.title = program_data["title"] 
        program.session_category = program_data["session_category"] 
        program.time_modified = timezone.now()
        program.save()
    else:
        participant_data["password"] = request_data["password"][0]
        participant = Participant.add(participant_data)

        participant_data["participant_id"] = participant.id
        program = Program.add(program_data)
    return redirect("../../registration_complete/")

@csrf_exempt
def registration_complete_view(request):
    return render(request, "program/registration_complete.html")

@csrf_exempt
def registration_edit_view(request):
    access_token = request.COOKIES.get('access_token')
    data_access_token = AccessToken.authorize(access_token)
    if not data_access_token:
        response = redirect("../login/?mode=reg")
        response.delete_cookie("access_token")
        return response
    else: 
        participant = Participant.get_by_id(id=data_access_token.participant_id)
        program = Program.get_by_participant_id(participant_id=participant.id)
        labs = Laboratory.objects.all()
        grades = Grade.objects.all()
        context = {
            "labs": labs,
            "grades": grades,
            "session_categories": settings["SESSION_CATEGORIES"],
            "user_info_participant": participant,
            "user_info_program": program,
            "settings": settings
        }
        print(context["user_info_participant"].__dict__)
        return render(request, "program/registration_edit.html", context=context)

@csrf_exempt
def signup_view(request):
    access_token = request.COOKIES.get('access_token')
    return redirect('../')
    #if access_token:
    #    return redirect('../')
    #else:
    #    labs = Laboratory.objects.all()
    #    grades = Grade.objects.all()
    #    context = {
    #        "labs": labs,
    #        "grades": grades
    #    }
    #    return render(request, "program/signup.html", context=context)

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
            response = redirect("../../registration_edit/")
        elif mode=="onsite":
            return redirect("../../")

        else: 
            if edit_active:
                return redirect("../../registration_edit/")
            else:
                return redirect("../../")

        response.set_cookie("access_token", access_token, max_age=60*60*24)
        return response

    else:
        return redirect("../../login/?mode={}&err=unauthorized".format(mode))

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
