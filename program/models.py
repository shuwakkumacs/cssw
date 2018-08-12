from django.db import models
import string
import hashlib
import random

# Create your models here.

class Grade(models.Model):
    display_name = models.CharField(max_length=10, default="")
    index = models.IntegerField(default=-1)

class Laboratory(models.Model):
    display_name = models.CharField(max_length=20, default="")
    display_name_en = models.CharField(max_length=20, default="")

class Participant(models.Model):
    surname = models.CharField(max_length=200, default="")
    givenname = models.CharField(max_length=200, default="")
    laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE, null=True)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, null=True)
    email = models.CharField(max_length=500, default="")
    password_md5 = models.CharField(max_length=200, default="")
    time_created = models.DateTimeField(auto_now_add=True, blank=True)
    time_modified = models.DateTimeField(blank=True, null=True)

    @staticmethod
    def get(email, password):
        return Participant.objects.filter(email=email, password_md5=md5(password)).first()

    @staticmethod
    def get_by_id(id):
        return Participant.objects.filter(id=id).first()

    @staticmethod
    def add(request_data):
        request_data["password_md5"] = md5(request_data["password"])
        del request_data["password"]
        data_participant = Participant(**request_data)
        data_participant.save()
        return data_participant

class AccessToken(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, null=True)
    access_token = models.CharField(max_length=100, default="")
    user_agent = models.TextField(default="")
    time_created = models.DateTimeField(auto_now_add=True, blank=True)

    def register(email, password, user_agent):
        participant = Participant.get(email, password)
        if participant:
            access_token = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(16))
            params = {
                "participant_id": participant.id,
                "access_token": access_token,
                "user_agent": user_agent
            }
            data_access_token = AccessToken(**params)
            data_access_token.save()
            return access_token
        else:
            return False

    def authorize(access_token):
        data_token = AccessToken.objects.filter(access_token=access_token).first()
        return data_token

class Program(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=300, default="")
    session_number = models.IntegerField(null=True, blank=True)
    program_number = models.IntegerField(null=True, blank=True)
    session_category = models.CharField(max_length=100,default="")
    time_created = models.DateTimeField(auto_now_add=True, blank=True)
    time_modified = models.DateTimeField(blank=True, null=True)

    def add(request_data):
        data_program = Program(**request_data)
        data_program.save()
        return data_program

    def get_by_participant_id(participant_id):
        return Program.objects.filter(participant_id=participant_id).first()

class ProgramHistory(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, null=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)
    liked = models.IntegerField(default=0)
    time_created = models.DateTimeField(auto_now_add=True, blank=True)
    time_liked = models.DateTimeField(blank=True, null=True)

    @staticmethod
    def get_all_for_participant(participant_id):
        return ProgramHistory.objects.filter(participant_id=participant_id).first()

class Vote(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, null=True)
    cancelled = models.IntegerField(default=0)
    time_created = models.DateTimeField(auto_now_add=True, blank=True)
    time_cancelled = models.DateTimeField(blank=True, null=True)

def md5(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()
