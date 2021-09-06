from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordChangeDoneView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('password-change-form/', PasswordChangeView.as_view(
         template_name='registration/password_change_form.html'),
         name='password_change_form'),
    path('password-change-done/', PasswordChangeDoneView.as_view(
         template_name='registration/password_change_done.html'),
         name='password_change_done'),
    path('signup/', views.SignUp.as_view(
         template_name='registration/signup.html'), name='signup'),
    path('logout/',
         LogoutView.as_view(template_name='registration/logged_out.html'),
         name='logout'),
    path('login/', LoginView.as_view(template_name='registration/login.html'),
         name='login'),
    path('password-reset-form/', PasswordResetView.as_view(
         template_name='registration/password_reset_form.html'),
         name='password_reset_form'),
    path('password-reset-complete/', PasswordResetCompleteView.as_view(
         template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(
         template_name='registration/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-done/', PasswordResetDoneView.as_view(
         template_name='registration/password_reset_done.html'),
         name='password_reset_done')
]
