from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/registration/login'}, name='logout'),
    url(r'^home/$', views.home, name='home'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^register/$', views.register, name='register'),
    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate, name='activate'),
    url(r'^account_activation_sent/$', TemplateView.as_view(template_name='registration/account_activation_sent.html')),
    url(r'^account_activation_invalid/', TemplateView.as_view(template_name='registration/account_activation_invalid.html')),
    url(r'^home/member_school_verification/$', views.member_school_verification_processing, name='member_school_verification_processing'),
    url(r'^home/member_school_verification_approve/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/(?P<school>.*)/$',
        views.member_school_verification_approve, name='member_school_verification_approve'),
    url(r'^home/member_school_verification_deny/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/(?P<school>.*)/$',
        views.member_school_verification_deny, name='member_school_verification_deny'),
    url(r'^member_school_verification_approved/$', TemplateView.as_view(template_name='registration/mem_school_verif_approved.html')),
    url(r'^member_school_verification_denied/$', TemplateView.as_view(template_name='registration/mem_school_verif_denied.html')),
    url(r'^member_school_verification_invalid/$', TemplateView.as_view(template_name='registration/mem_school_verif_invalid.html')),
    url(r'^ajax/is_conference_full/$', views.is_conference_full, name='is_conference_full'),
    url(r'^ajax/update_paid_attendee/$', views.update_paid_attendee, name='update_paid_attendee'),
    url(r'^home/refund_registration/$', views.refund_registration, name='refund_registration'),
    url(r'^home/reg_refund/$', login_required(TemplateView.as_view(template_name='registration/reg_refund.html')), name='reg_refund'),
    url(r'^home/reg_refund_complete/$', login_required(TemplateView.as_view(template_name='registration/reg_refund_complete.html')), name='reg_refund_complete'),
    url(r'^ajax/validate_trans_id/$', views.validate_trans_id, name='validate_trans_id'),
]
