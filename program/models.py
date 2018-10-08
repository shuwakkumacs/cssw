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
    affiliation = models.CharField(max_length=50, blank=True, verbose_name="ご所属 Affiliation")
    reference = models.CharField(max_length=50, blank=True, verbose_name="紹介者 Reference name")
    email = models.CharField(max_length=500, default="", verbose_name="Eメールアドレス Email address")
    password = models.CharField(max_length=200, default="", verbose_name="パスワード Password")
    is_presenter = models.CharField(max_length=10, choices=PRESENTER_CHOICES, verbose_name="発表の有無 Are you a presenter?")
    party_attendance = models.CharField(max_length=10, choices=PARTY_ATTENDANCE_CHOICES, verbose_name="懇親会の参加 Dinner party")
    food_restriction = models.CharField(max_length=10, choices=FOOD_RESTRICTION_CHOICES, verbose_name="食物制限の有無 Do you have any food restriction?")
    comment = models.TextField(blank=True)
    is_admin = models.BooleanField(default=False)
    time_created = models.DateTimeField(auto_now_add=True, blank=True)
    time_modified = models.DateTimeField(blank=True, null=True)
    time_deleted = models.DateTimeField(blank=True, null=True)

    @staticmethod
    def get(email, password):
        return Participant.objects.filter(email=email, password=md5(password), time_deleted=None).first()

    @staticmethod
    def get_by_id(id):
        return Participant.objects.filter(id=id, time_deleted=None).first()

    @staticmethod
    def get_by_email(email):
        return Participant.objects.filter(email=email, time_deleted=None).first()

    @staticmethod
    def add(request_data):
        request_data["password"] = md5(request_data["password"])
        del request_data["password"]
        data_participant = Participant(**request_data)
        data_participant.save()
        return data_participant

    @staticmethod
    def delete_by_id(id=id):
        participant = Participant.get_by_id(id)
        participant.time_deleted = timezone.now()
        participant.save()

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
                "user_agent": user_agent,
            }
            data_access_token = AccessToken(**params)
            data_access_token.save()
            return access_token
        else:
            return False

    def authorize(access_token,admin=False):
        data_token = AccessToken.objects.filter(access_token=access_token).first()
        return data_token

class Program(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=300, default="", verbose_name="表題 Title")
    session_number = models.CharField(max_length=10, null=True, blank=True, verbose_name="セッション番号 Session number")
    program_number = models.IntegerField(null=True, blank=True, verbose_name="プログラム番号 Program number")
    session_category = models.CharField(max_length=100, choices=SESSION_CATEGORY_CHOICES, verbose_name="セッション種別 Session category")
    require_table = models.CharField(max_length=10, choices=REQUIRE_TABLE_CHOICES, verbose_name="デモ用テーブルの用意 Demo table")
    co_presenters = models.CharField(max_length=300, null=True, blank=True, verbose_name="共同発表者 Co-presenters")
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

    def get_by_program_number(session_number,program_number):
        return Program.objects.filter(session_number=session_number, program_number=program_number).first()

    def delete_by_id(id):
        program = Program.objects.filter(id=id).first()
        program.time_deleted = timezone.now()
        program.save()
        return program

    def delete_by_participant_id(participant_id):
        programs = Program.objects.filter(participant_id=participant_id).all()
        for program in programs:
            program.time_deleted = timezone.now()
            program.save()
        return programs

    @staticmethod
    def get_with_participants(laboratory="",grade="",session_category=""):
        laboratory_query = ""
        grade_query = ""
        session_category_query = ""
        if laboratory:
            laboratory_query = " and pa.laboratory='{}'".format(laboratory)
        if grade:
            grade_query = " and pa.grade='{}'".format(grade)
        if session_category:
            session_category_query = " and pr.session_category='{}'".format(session_category)
        data_all = Program.objects.raw("select pa.*,pr.* from program_participant as pa left join (select * from program_program where time_deleted is null) as pr on pa.id=pr.participant_id where pa.time_deleted is null{}{}{} order by pa.id;".format(laboratory_query,grade_query,session_category_query))
        return data_all

class ProgramHistory(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, null=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)
    time_created = models.DateTimeField(auto_now_add=True, blank=True)

    @staticmethod
    def add(participant,program):
        program_history = ProgramHistory(participant=participant, program=program).save()
        return program_history

    #@staticmethod
    #def get_all_for_participant(participant_id,desc=True):
    #    hists = ProgramHistory.objects.filter(participant_id=participant_id)
    #    if desc:
    #        return hists.order_by("-id").all()
    #    else:
    #        return hists.all()
    
    @staticmethod
    def get_all_for_participant_with_points(participant_id,order="desc"):
        return ProgramHistory.objects.raw("select p.id,p.program_id,v.point from program_programhistory as p left join (select tmp1.* from program_votehistory as tmp1 inner join (select program_id,max(time_created) as max_time_created from program_votehistory group by participant_id,program_id) as tmp2 on (tmp1.program_id=tmp2.program_id and tmp1.time_created=tmp2.max_time_created)) as v on (p.participant_id=v.participant_id and p.program_id=v.program_id) where p.participant_id={} order by p.program_id {};".format(participant_id,order))

    @staticmethod
    def get_by_program_id(participant,program_id):
        return ProgramHistory.objects.filter(participant=participant,program_id=program_id).first()

class VoteHistory(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, null=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)
    point = models.IntegerField(default=0)
    time_created = models.DateTimeField(auto_now_add=True, blank=True)

    @staticmethod
    def add(participant,program_id,point):
        vote = VoteHistory(participant=participant,program_id=program_id,point=point).save()
        return vote

    @staticmethod
    def get_latest_by_program_id(participant,program_id):
        return VoteHistory.objects.filter(participant=participant,program_id=program_id).order_by("-time_created").first()

class PasswordResetSession(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, null=True)
    reset_token = models.CharField(max_length=100, default="")
    time_created = models.DateTimeField(auto_now_add=True, blank=True)
    time_completed = models.DateTimeField(blank=True, null=True)

    @staticmethod
    def add(participant):
        reset_token = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(16))
        PasswordResetSession(participant=participant,reset_token=reset_token).save()
        return reset_token

    @staticmethod
    def get_by_id(id):
        return PasswordResetSession.objects.filter(id=id).first()

    @staticmethod
    def get(reset_token):
        return PasswordResetSession.objects.filter(reset_token=reset_token).last()

    @staticmethod
    def change_password(id,password):
        session = PasswordResetSession.get_by_id(id=id)
        if session.time_completed is not None:
            return False
        try:
            now = timezone.now()
            participant = session.participant
            participant.password = md5(password)
            participant.time_modified = now
            participant.save()
            session.time_completed = now
            session.save()
            return True
        except Exception as e:
            print(e)
            return False

def md5(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()
