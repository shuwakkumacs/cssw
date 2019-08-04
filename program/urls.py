from django.conf.urls import url

from . import views

app_name="program"
urlpatterns = [
    url(r'^registration/$', views.registration_view),  # 参加登録画面
    url(r'^registration_complete/$', views.registration_complete_view),  # 参加登録終了画面
    url(r'^login/$', views.login_view),  # ログイン画面
    url(r'^registration_list/$', views.registration_list_view),  # 参加登録一覧管理画面（要ログイン）
    url(r'^password_forget/$', views.password_forget_view),  # パスワード再発行用メールアドレス入力画面
    url(r'^password_change/(?P<reset_token>\w{1,100})/$', views.password_change_view),  # パスワード変更画面（メールから誘導）
    url(r'^program_history/$', views.program_history_view),  # スキャン済み発表プログラム一覧出力画面
    url(r'^operation/registration/$', views.registration),
    url(r'^operation/qrscan/(?P<hash_code>\S{1,100})/$', views.qrscan),
    url(r'^operation/signup/$', views.signup),
    url(r'^operation/login/$', views.login),
    url(r'^operation/logout/$', views.logout),
    url(r'^operation/delete_program/$', views.delete_program),
    url(r'^operation/registration_list/$', views.get_registration_list),
    url(r'^operation/email/password_reset/$', views.send_email__password_reset),
    url(r'^operation/password_change/$', views.password_change),
    url(r'^operation/vote/(?P<program_id>[0-9]{1,5})/(?P<point>[0-9]{1,5})/$', views.vote),
]
