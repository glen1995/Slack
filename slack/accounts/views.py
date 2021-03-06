from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

#Using the inbuilt signup function and pointing it to the respected html file
class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'
