from django.db import models
import string
import hashlib
import random
from django.utils import timezone

GRADE_CHOICES = (
    ("D", "D"),
    ("M2", "M2"),
    ("M1", "M1"),
    ("B4", "B4"),
    ("B3", "B3-"),
    ("F", "教員 Faculty"),
    ("A", "OB/OG Alumnus"),
    ("N/A", "該当なし N/A")
)

LABORATORY_CHOICES = (
    ("Ishikawa", "石川研 Ishikawa Lab."),
    ("Ogawa", "小川研 Ogawa Lab."),
    ("Katto", "甲藤研 Katto Lab."),
    ("Kobayashi", "小林研 Kobayashi Lab."),
    ("Sakai", "酒井研 Sakai Lab."),
    ("Shimizu", "清水研 Shimizu Lab."),
    ("Nakajima", "中島研 Nakajima Lab."),
    ("Yamana", "山名研 Yamana Lab."),
    ("N/A", "該当なし N/A")
)

PRESENTER_CHOICES = (
    ("Yes", "あり Yes"),
    ("No", "なし No")
)

FOOD_RESTRICTION_CHOICES = (
    ("Yes", "あり Yes"),
    ("No", "なし No")
)

REQUIRE_TABLE_CHOICES = (
    ("No", "不要 No, I don't need one"),
    ("Yes", "必要 Yes, I need one")
)

PARTY_ATTENDANCE_CHOICES = (
    ("Yes", "する Yes, I participate"),
    ("No", "しない No, I don't participate")
)

SESSION_CATEGORY_CHOICES = (
    ("Technical", "Technical"),
    ("WiP", "Work-in-Progress"),
    ("Short", "Short Project")
)

class Participant(models.Model):
    surname = models.CharField(max_length=50, default="", verbose_name="姓", blank=True)
    givenname = models.CharField(max_length=50, default="", verbose_name="名")
    surname_en = models.CharField(max_length=50, default="", verbose_name="Surname", blank=True)
    givenname_en = models.CharField(max_length=50, default="", verbose_name="Given name")
    laboratory = models.CharField(max_length=50, choices=LABORATORY_CHOICES, verbose_name="所属研究室 Laboratory")
    grade = models.CharField(max_length=10, choices=GRADE_CHOICES, verbose_name="学年 Grade")
    email = models.CharField(max_length=500, default="", verbose_name="Eメールアドレス Email address")
    password = models.CharField(max_length=200, default="", verbose_name="パスワード Password")
    is_presenter = models.CharField(max_length=10, choices=PRESENTER_CHOICES, verbose_name="発表の有無 Are you a presenter?")
    party_attendance = models.CharField(max_length=10, choices=PARTY_ATTENDANCE_CHOICES, verbose_name="懇親会の参加 Dinner party")
    food_restriction = models.CharField(max_length=10, choices=FOOD_RESTRICTION_CHOICES, verbose_name="食物制限の有無 Do you have any food restriction?")
    comment = models.TextField(blank=True)
    time_created = models.DateTimeField(auto_now_add=True, blank=True)
    time_modified = models.DateTimeField(blank=True, null=True)

    @staticmethod
    def get(email, password):
        return Participant.objects.filter(email=email, password=md5(password)).first()

    @staticmethod
    def get_by_id(id):
        return Participant.objects.filter(id=id).first()

    @staticmethod
    def add(request_data):
        request_data["password"] = md5(request_data["password"])
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
    title = models.CharField(max_length=300, default="", verbose_name="表題 Title")
    session_number = models.IntegerField(null=True, blank=True, verbose_name="セッション番号 Session number")
    program_number = models.IntegerField(null=True, blank=True, verbose_name="プログラム番号 Program number")
    session_category = models.CharField(max_length=100, choices=SESSION_CATEGORY_CHOICES, verbose_name="セッション種別 Session category")
    require_table = models.CharField(max_length=10, choices=REQUIRE_TABLE_CHOICES, verbose_name="デモ用テーブルの用意 Demo table")
    time_created = models.DateTimeField(auto_now_add=True, blank=True)
    time_modified = models.DateTimeField(blank=True, null=True)
    time_deleted = models.DateTimeField(blank=True, null=True)

    def add(request_data):
        data_program = Program(**request_data)
        data_program.save()
        return data_program

    def get_by_id(id):
        return Program.objects.filter(id=id).first()

    def get_by_participant_id(participant_id):
        return Program.objects.filter(participant_id=participant_id, time_deleted=None).all()

    def delete_by_id(id):
        print(id)
        program = Program.objects.filter(id=id).first()
        program.time_deleted = timezone.now()
        program.save()
        return program

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
