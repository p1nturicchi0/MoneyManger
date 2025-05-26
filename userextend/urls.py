from django.urls import path
from userextend import views
from .views import CustomPasswordChangeView,CustomPasswordChangeDoneView,CustomPasswordResetView,CustomPasswordResetDoneView,CustomPasswordResetConfirmView,CustomPasswordResetCompleteView

urlpatterns =   [
    path('create_user/', views.UserCreateView.as_view(), name='create_user'),

    path("change_password/", CustomPasswordChangeView.as_view(), name="change_password"),
    path("password_change_done/", CustomPasswordChangeDoneView.as_view(), name="password_change_done"),
    path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path("password_reset_done/", CustomPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", CustomPasswordResetCompleteView.as_view(), name="password_reset_complete"),
]



