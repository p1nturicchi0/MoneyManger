
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.views.generic import CreateView
import random
from MoneyManagerDanut.settings import DEFAULT_FROM_EMAIL
from userextend.forms import UserForm

# Create an account for our aplication
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

            # We create an username for our user
            username = random.randint(100000, 999999)
            new_user.username = f"{new_user.first_name[0].lower()}{new_user.last_name.lower()}_{username}"
            new_user.save()

            # We send an e-mail after registration
            subject = 'Money Manager - username created'
            mesaj = (f"Hello, {new_user.first_name} {new_user.last_name}\n\n"
                     f"Welcome to Money Manager App! To log in, here is your username: \nusername: {new_user.username}")

            send_mail(subject, mesaj, DEFAULT_FROM_EMAIL, [new_user.email])

        return super(UserCreateView, self).form_valid(form)