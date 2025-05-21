from django.views.generic import TemplateView

# We use TmplateView to show our homepage on the application
class HomeTemplateView(TemplateView):
    template_name = 'home/homepage.html'

