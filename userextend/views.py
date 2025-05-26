import random
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, PasswordResetCompleteView, PasswordResetConfirmView
from django.core.mail import send_mail
from django.views.generic import CreateView
from MoneyManagerDanut.settings import DEFAULT_FROM_EMAIL
from userextend.forms import UserForm, UserPasswordResetForm, PasswordChangedForm


# Create an account for our application
class UserCreateView(CreateView):
    template_name = 'userextend/create_user.html'
    model = User
    form_class= UserForm
    success_url = '/login/'

    def form_valid(self, form):
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.first_name = new_user.first_name.title()
            new_user.last_name = new_user.last_name.title()

            # We create a username for our user
            username = random.randint(100000, 999999)
            new_user.username = f"{new_user.first_name[0].lower()}{new_user.last_name.lower()}_{username}"
            new_user.save()

            # We send an e-mail after registration
            subject = 'Money Manager - username created'
            mesage = (f"Hello, {new_user.first_name} {new_user.last_name}\n\n"
                     f"Welcome to Money Manager App! To log in, here is your username: \nusername: {new_user.username}")

            send_mail(subject, mesage, DEFAULT_FROM_EMAIL, [new_user.email])

        return super(UserCreateView, self).form_valid(form)

# Users can change their password
class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'registration/password_change_form.html'
    form_class = PasswordChangedForm
    success_url = '/password_change_done/'

# Validation page after password has been changed
class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'registration/password_change_done.html'


# Users can reset their password if they forgot it
class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    form_class = UserPasswordResetForm
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = '/password_reset_done/'

# # Validation page after confirmation link has been sent to the user`s email
class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'

# A verification link sent on user`s email in order to reset their password
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = '/password_reset_complete/'

# Validation page after password has been reseted
class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'

